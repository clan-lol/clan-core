import logging
from dataclasses import dataclass

from clan_lib.api import MethodRegistry

from clan_app.api.api_bridge import BackendResponse

from .base import Middleware, MiddlewareContext, MiddlewareError

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class MethodExecutionMiddleware(Middleware):
    """Middleware that handles actual method execution."""

    api: MethodRegistry

    def process(self, context: MiddlewareContext) -> None:
        method = self.api.functions[context.request.method_name]

        try:
            # Execute the actual method
            result = method(**context.request.args)

            response = BackendResponse(
                body=result,
                header={},
                _op_key=context.request.op_key or "unknown",
            )
            context.bridge.send_api_response(response)

        except Exception as e:
            # Create enhanced exception with original calling context
            enhanced_error = MiddlewareError(
                f"Error in method '{context.request.method_name}'",
                context.original_traceback,
                e,
            )

            # Chain the exceptions to preserve both tracebacks
            raise enhanced_error from e
