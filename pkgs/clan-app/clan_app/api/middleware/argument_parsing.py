import logging
from dataclasses import dataclass

from clan_lib.api import MethodRegistry, from_dict

from clan_app.api.api_bridge import BackendRequest

from .base import Middleware, MiddlewareContext

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
                if k == "op_key":
                    continue

                # Get the expected argument type from the API
                arg_class = self.api.get_method_argtype(context.request.method_name, k)

                # Convert dictionary to dataclass instance
                reconciled_arguments[k] = from_dict(arg_class, v)

            # Add op_key to arguments
            reconciled_arguments["op_key"] = context.request.op_key

            # Create a new request with reconciled arguments

            updated_request = BackendRequest(
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
