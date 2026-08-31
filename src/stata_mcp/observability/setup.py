"""MCP server startup configuration for local diagnostics."""

from __future__ import annotations

import logging
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from .checkpoints import CheckpointWriter, configure_checkpoint_writer
from .exporter import LocalJsonlSpanExporter

logger = logging.getLogger(__name__)
_configured_provider: TracerProvider | None = None


def configure_local_observability(
    artifact_root: str | Path,
    *,
    enabled: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 3,
) -> bool:
    """Configure default-on local checkpoints and completed-span export."""
    global _configured_provider

    if not enabled:
        configure_checkpoint_writer(None)
        return False

    configure_checkpoint_writer(
        CheckpointWriter(
            artifact_root,
            max_bytes=max_bytes,
            backup_count=backup_count,
        )
    )
    if _configured_provider is not None:
        return True

    current_provider = trace.get_tracer_provider()
    if isinstance(current_provider, TracerProvider):
        provider = current_provider
    else:
        provider = TracerProvider(
            resource=Resource.create({"service.name": "stata-mcp"})
        )
        try:
            trace.set_tracer_provider(provider)
        except Exception as error:
            logger.warning(
                "Local OpenTelemetry setup was skipped: %s",
                type(error).__name__,
            )
            return False
        if trace.get_tracer_provider() is not provider:
            logger.warning("Local OpenTelemetry setup was skipped: provider is fixed")
            return False

    exporter = LocalJsonlSpanExporter(
        artifact_root,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    _configured_provider = provider
    return True
