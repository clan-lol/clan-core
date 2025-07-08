import io
import json
import logging
from abc import ABC, abstractmethod
from contextlib import ExitStack
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ContextManager

from clan_lib.api import MethodRegistry, dataclass_to_dict, from_dict
from clan_lib.async_run import AsyncContext, get_async_ctx, set_async_ctx
from clan_lib.custom_logger import setup_logging
from clan_lib.log_manager import LogManager

from .api_bridge import ApiRequest, ApiResponse

if TYPE_CHECKING:
    from .api_bridge import ApiBridge, ApiRequest

log = logging.getLogger(__name__)


@dataclass
class MiddlewareContext:
    request: "ApiRequest"
    bridge: "ApiBridge"
    exit_stack: ExitStack


@dataclass(frozen=True)
class Middleware(ABC):
    """Abstract base class for middleware components."""

    @abstractmethod
    def process(self, context: MiddlewareContext) -> None:
        """Process the request through this middleware."""

    def register_context_manager(
        self, context: MiddlewareContext, cm: ContextManager[Any]
    ) -> Any:
        """Register a context manager with the exit stack."""
        return context.exit_stack.enter_context(cm)


@dataclass(frozen=True)
class ArgumentParsingMiddleware(Middleware):
    """Middleware that handles argument parsing and dataclass construction."""

    api: MethodRegistry

    def process(self, context: MiddlewareContext) -> None:
        try:
            # Convert dictionary arguments to dataclass instances
            reconciled_arguments = {}
            for k, v in context.request.args.items():
                if k == "op_key":
                    continue

                # Get the expected argument type from the API
                arg_class = self.api.get_method_argtype(context.request.method_name, k)

                # Convert dictionary to dataclass instance
                reconciled_arguments[k] = from_dict(arg_class, v)

            # Add op_key to arguments
            reconciled_arguments["op_key"] = context.request.op_key

            # Create a new request with reconciled arguments

            updated_request = ApiRequest(
                method_name=context.request.method_name,
                args=reconciled_arguments,
                header=context.request.header,
                op_key=context.request.op_key,
            )
            context.request = updated_request

        except Exception as e:
            log.exception(
                f"Error while parsing arguments for {context.request.method_name}"
            )
            context.bridge.send_error_response(
                context.request.op_key,
                str(e),
                ["argument_parsing", context.request.method_name],
            )
            raise


@dataclass(frozen=True)
class LoggingMiddleware(Middleware):
    """Middleware that sets up logging context without executing methods."""

    log_manager: LogManager

    def process(self, context: MiddlewareContext) -> None:
        method = context.request.method_name

        try:
            # Handle log group configuration
            log_group: list[str] | None = context.request.header.get("logging", {}).get(
                "group_path", None
            )
            if log_group is not None:
                if not isinstance(log_group, list):
                    msg = f"Expected log_group to be a list, got {type(log_group)}"
                    raise TypeError(msg)
                log.warning(
                    f"Using log group {log_group} for {context.request.method_name} with op_key {context.request.op_key}"
                )
            # Create log file
            log_file = self.log_manager.create_log_file(
                method, op_key=context.request.op_key, group_path=log_group
            ).get_file_path()

        except Exception as e:
            log.exception(
                f"Error while handling request header of {context.request.method_name}"
            )
            context.bridge.send_error_response(
                context.request.op_key,
                str(e),
                ["header_middleware", context.request.method_name],
            )
            return

        # Register logging context manager
        class LoggingContextManager:
            def __init__(self, log_file) -> None:
                self.log_file = log_file
                self.log_f = None
                self.handler = None
                self.original_ctx = None

            def __enter__(self):
                self.log_f = self.log_file.open("ab")
                self.original_ctx = get_async_ctx()

                # Set up async context for logging
                ctx = AsyncContext(**self.original_ctx.__dict__)
                ctx.stderr = self.log_f
                ctx.stdout = self.log_f
                set_async_ctx(ctx)

                # Set up logging handler
                handler_stream = io.TextIOWrapper(
                    self.log_f,
                    encoding="utf-8",
                    write_through=True,
                    line_buffering=True,
                )
                self.handler = setup_logging(
                    log.getEffectiveLevel(), log_file=handler_stream
                )

                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.handler:
                    self.handler.root_logger.removeHandler(self.handler.new_handler)
                    self.handler.new_handler.close()
                if self.log_f:
                    self.log_f.close()
                if self.original_ctx:
                    set_async_ctx(self.original_ctx)

        # Register the logging context manager
        self.register_context_manager(context, LoggingContextManager(log_file))


@dataclass(frozen=True)
class MethodExecutionMiddleware(Middleware):
    """Middleware that handles actual method execution."""

    api: MethodRegistry

    def process(self, context: MiddlewareContext) -> None:
        method = self.api.functions[context.request.method_name]

        try:
            # Execute the actual method
            result = method(**context.request.args)
            wrapped_result = {"body": dataclass_to_dict(result), "header": {}}

            log.debug(
                f"Result for {context.request.method_name}: {json.dumps(dataclass_to_dict(wrapped_result), indent=4)}"
            )

            response = ApiResponse(
                op_key=context.request.op_key, success=True, data=wrapped_result
            )
            context.bridge.send_response(response)

        except Exception as e:
            log.exception(
                f"Error while handling result of {context.request.method_name}"
            )
            context.bridge.send_error_response(
                context.request.op_key,
                str(e),
                ["method_execution", context.request.method_name],
            )
