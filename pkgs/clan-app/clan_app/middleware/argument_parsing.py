import logging
from dataclasses import dataclass

from clan_lib.api import MethodRegistry, from_dict

from clan_app.api.api_bridge import BackendRequest

from .base import Middleware, MiddlewareContext, MiddlewareError

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ArgumentParsingMiddleware(Middleware):
    """Middleware that handles argument parsing and dataclass construction."""

    api: MethodRegistry

    def process(self, context: MiddlewareContext) -> None:
        try:
            # Convert dictionary arguments to dataclass instances
            reconciled_arguments = {}
            for k, v in context.request.args.items():
                # Get the expected argument type from the API
                arg_class = self.api.get_method_argtype(context.request.method_name, k)
                # Convert dictionary to dataclass instance
                reconciled_arguments[k] = from_dict(arg_class, v)

            # Create a new request with reconciled arguments
            updated_request = BackendRequest(
                method_name=context.request.method_name,
                args=reconciled_arguments,
                header=context.request.header,
                op_key=context.request.op_key,
            )
            context.request = updated_request

        except Exception as e:
            # Create enhanced exception with original calling context
            enhanced_error = MiddlewareError(
                f"Error in method '{context.request.method_name}'",
                context.original_traceback,
                e,
            )

            # Chain the exceptions to preserve both tracebacks
            raise enhanced_error from e
