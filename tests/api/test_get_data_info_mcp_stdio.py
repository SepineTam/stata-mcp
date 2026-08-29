"""End-to-end stdio protocol regression tests for get_data_info."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import anyio
import pytest
from mcp import Client, StdioServerParameters


@pytest.mark.parametrize(
    ("mode", "expected_protocol"),
    [
        ("auto", "2026-07-28"),
        ("legacy", "2025-11-25"),
    ],
)
def test_get_data_info_stdio_schema_and_response_remain_compatible(
    tmp_path: Path,
    mode: str,
    expected_protocol: str,
) -> None:
    """Diagnostic logging must not alter schema, structured output, or stdio framing."""
    working_dir = tmp_path / "workspace"
    working_dir.mkdir()
    data_path = working_dir / "sample.csv"
    data_path.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[DEBUG.logging]",
                "LOGGING_ON = false",
                "",
                "[BETA]",
                "enable_windows_data_info = true",
                "",
                "[PROJECT]",
                f'WORKING_DIR = "{working_dir.as_posix()}"',
                "",
                "[data_info]",
                "is_cache = false",
            ]
        ),
        encoding="utf-8",
    )

    async def _run_protocol_test() -> None:
        server = StdioServerParameters(
            command=sys.executable,
            args=[
                "-c",
                "from stata_mcp.cli import main; main()",
                "-c",
                str(config_path),
            ],
            cwd=str(working_dir),
        )
        async with Client(server, mode=mode) as client:
            protocol_version = client.protocol_version
            listed_tools = await client.list_tools()
            tool = next(item for item in listed_tools.tools if item.name == "get_data_info")
            result = await client.call_tool(
                "get_data_info",
                {"data_path": str(data_path)},
            )

        assert protocol_version == expected_protocol
        assert set(tool.input_schema["properties"]) == {
            "data_path",
            "vars_list",
            "encoding",
            "head",
        }
        assert tool.output_schema["properties"]["result"]["type"] == "string"
        assert result.is_error is False
        assert result.structured_content is not None
        text_result = result.content[0].text
        assert result.structured_content["result"] == text_result
        assert json.loads(text_result)["overview"]["obs"] == 2

    anyio.run(_run_protocol_test)
