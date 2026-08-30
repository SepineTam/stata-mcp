"""Rotating local JSONL checkpoints that never control tool execution."""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Mapping, Protocol

logger = logging.getLogger(__name__)


class CheckpointSink(Protocol):
    """Minimal sink interface used by diagnostic steps."""

    def append(self, payload: Mapping[str, Any]) -> bool:
        """Append one record and report whether persistence succeeded."""


class CheckpointWriter:
    """Append privacy-safe checkpoints to a bounded local JSONL file."""

    def __init__(
        self,
        artifact_root: str | Path,
        *,
        filename: str = "checkpoints.jsonl",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 3,
    ) -> None:
        self.path = Path(artifact_root) / "debug" / filename
        self.max_bytes = max(0, int(max_bytes))
        self.backup_count = max(0, int(backup_count))
        self._lock = threading.Lock()

    def append(self, payload: Mapping[str, Any]) -> bool:
        """Write one checkpoint without propagating diagnostic failures."""
        try:
            from ..audit.redaction import redact_value

            normalized = redact_value(dict(payload))
            line = json.dumps(
                normalized,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            encoded_size = len((line + "\n").encode("utf-8"))
            with self._lock:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self._rotate_if_needed(encoded_size)
                with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                    stream.write(line + "\n")
                    stream.flush()
            return True
        except Exception as error:
            logger.warning(
                "Diagnostic checkpoint was not persisted: %s",
                type(error).__name__,
            )
            return False

    def _rotate_if_needed(self, incoming_size: int) -> None:
        if self.max_bytes <= 0 or not self.path.exists():
            return
        if self.path.stat().st_size + incoming_size <= self.max_bytes:
            return
        if self.backup_count == 0:
            self.path.unlink(missing_ok=True)
            return

        oldest = self._backup_path(self.backup_count)
        oldest.unlink(missing_ok=True)
        for index in range(self.backup_count - 1, 0, -1):
            source = self._backup_path(index)
            if source.exists():
                source.replace(self._backup_path(index + 1))
        self.path.replace(self._backup_path(1))

    def _backup_path(self, index: int) -> Path:
        return self.path.with_name(f"{self.path.name}.{index}")


_checkpoint_writer: CheckpointSink | None = None


def configure_checkpoint_writer(writer: CheckpointSink | None) -> None:
    """Set the process-local checkpoint sink used by debug steps."""
    global _checkpoint_writer
    _checkpoint_writer = writer


def current_checkpoint_writer() -> CheckpointSink | None:
    """Return the configured checkpoint sink, if any."""
    return _checkpoint_writer


def write_checkpoint(payload: Mapping[str, Any]) -> bool:
    """Append one checkpoint through the configured fail-open sink."""
    writer = current_checkpoint_writer()
    if writer is None:
        return False
    try:
        return bool(writer.append(payload))
    except Exception:
        return False
