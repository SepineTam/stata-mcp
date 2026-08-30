"""MCP v2 middleware for durable tools/call audit events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Mapping

from .context import bind_audit_context
from .models import AuditExecutionContext
from .store import AuditStore

if TYPE_CHECKING:
    from mcp.server.context import HandlerResult, ServerRequestContext

CallNext = Callable[[Any], Awaitable[Any]]


class AuditMiddleware:
    """Record MCP tool lifecycle events without changing tool responses."""

    def __init__(self, store: AuditStore):
        self.store = store

    async def __call__(
        self,
        context: ServerRequestContext,
        call_next: CallNext,
    ) -> HandlerResult:
        if context.method != "tools/call":
            return await call_next(context)

        parameters = dict(context.params or {})
        tool = str(parameters.get("name") or "unknown_tool")
        arguments = parameters.get("arguments")
        if not isinstance(arguments, Mapping):
            arguments = {}
        source_reference = self._source_reference(tool, arguments)
        run = self.store.start_run(
            tool=tool,
            source_reference=source_reference,
            input_payload=arguments,
            interface="mcp",
            client=self._client_info(context),
            protocol_version=getattr(context, "protocol_version", None),
            request_id=self._request_id(context),
        )
        execution_context = AuditExecutionContext(run=run, store=self.store)

        try:
            with bind_audit_context(execution_context):
                result = await call_next(context)
        except BaseException as error:
            self.store.finish_run(
                run,
                event=(
                    execution_context.terminal_event
                    or (
                        "interrupted"
                        if isinstance(error, KeyboardInterrupt)
                        else "failed"
                    )
                ),
                artifacts=execution_context.artifacts,
                error={"type": type(error).__name__, "message": str(error)},
                security_event_ids=execution_context.security_event_ids,
                executed=execution_context.terminal_event != "blocked",
            )
            raise

        is_error = bool(
            getattr(result, "is_error", False)
            or (isinstance(result, Mapping) and result.get("isError"))
        )
        self.store.finish_run(
            run,
            event=(
                execution_context.terminal_event
                or ("failed" if is_error else "completed")
            ),
            artifacts=execution_context.artifacts,
            output={"is_error": is_error},
            security_event_ids=execution_context.security_event_ids,
            executed=execution_context.terminal_event != "blocked",
        )
        return result

    @staticmethod
    def _source_reference(tool: str, arguments: Mapping[str, Any]) -> str:
        for key in ("dofile_path", "data_path", "file_path"):
            value = arguments.get(key)
            if isinstance(value, (str, bytes)):
                return value.decode() if isinstance(value, bytes) else value
        return tool

    @staticmethod
    def _client_info(context: Any) -> dict[str, Any] | None:
        session = getattr(context, "session", None)
        client_parameters = getattr(session, "client_params", None)
        client_info = getattr(client_parameters, "client_info", None)
        if client_info is None:
            return None
        if hasattr(client_info, "model_dump"):
            return client_info.model_dump(mode="json", exclude_none=True)
        if isinstance(client_info, Mapping):
            return dict(client_info)
        return {
            "name": getattr(client_info, "name", "unknown"),
            "version": getattr(client_info, "version", "unknown"),
        }

    @staticmethod
    def _request_id(context: Any) -> str | None:
        request_id = getattr(context, "request_id", None)
        return None if request_id is None else str(request_id)
