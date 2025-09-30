import io
import logging
import os
import sys
import types
from dataclasses import dataclass
from typing import Any

from clan_lib.async_run import AsyncContext, get_async_ctx, set_async_ctx
from clan_lib.custom_logger import RegisteredHandler, setup_logging
from clan_lib.log_manager import LogManager

from .base import Middleware, MiddlewareContext, MiddlewareError

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoggingMiddleware(Middleware):
    """Middleware that sets up logging context without executing methods."""

    log_manager: LogManager

    def process(self, context: MiddlewareContext) -> None:
        method = context.request.method_name

        try:
            # Handle log group configuration
            log_group: list[str] | None = context.request.header.get("logging", {}).get(
                "group_path",
                None,
            )
            if log_group is not None:
                if not isinstance(log_group, list):
                    msg = f"Expected log_group to be a list, got {type(log_group)}"
                    raise TypeError(msg)  # noqa: TRY301
                log.warning(
                    f"Using log group {log_group} for {context.request.method_name} with op_key {context.request.op_key}",
                )
            # Create log file
            log_file = self.log_manager.create_log_file(
                method,
                op_key=context.request.op_key or "unknown",
                group_path=log_group,
            ).get_file_path()

        except Exception as e:
            # Create enhanced exception with original calling context
            enhanced_error = MiddlewareError(
                f"Error in method '{context.request.method_name}'",
                context.original_traceback,
                e,
            )

            # Chain the exceptions to preserve both tracebacks
            raise enhanced_error from e

        # Register logging context manager
        class LoggingContextManager:
            def __init__(self, log_file: Any) -> None:
                self.log_file = log_file
                self.log_f: Any = None
                self.handler: RegisteredHandler | None = None
                self.original_ctx: AsyncContext | None = None

            def __enter__(self) -> "LoggingContextManager":
                self.log_f = self.log_file.open("ab")
                self.original_ctx = get_async_ctx()

                # Set up async context for logging
                ctx = AsyncContext(**self.original_ctx.__dict__)
                ctx.stderr = self.log_f
                ctx.stdout = self.log_f
                set_async_ctx(ctx)

                # Set up logging handler
                handler_stream = io.TextIOWrapper(
                    self.log_f,  # type: ignore[arg-type]
                    encoding="utf-8",
                    write_through=True,
                    line_buffering=True,
                )
                self.handler = setup_logging(
                    log.getEffectiveLevel(),
                    log_file=handler_stream,
                )

                return self

            def __exit__(
                self,
                exc_type: type[BaseException] | None,
                exc_val: BaseException | None,
                exc_tb: types.TracebackType | None,
            ) -> None:
                orig_stderr = None
                if self.handler:
                    self.handler.root_logger.removeHandler(self.handler.new_handler)
                    self.handler.new_handler.close()
                if self.original_ctx:
                    set_async_ctx(self.original_ctx)
                    orig_stderr = self.original_ctx.stderr
                if self.log_f:
                    # Replace the file descriptor instead of closing it
                    stderr = orig_stderr or sys.stderr
                    new_fd = stderr.fileno()
                    os.dup2(self.log_f.fileno(), new_fd)
                    self.log_f.close()

        # Register the logging context manager
        self.register_context_manager(context, LoggingContextManager(log_file))
