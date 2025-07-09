import logging
from dataclasses import dataclass

from clan_lib.api import MethodRegistry

from clan_app.api.api_bridge import BackendResponse

from .base import Middleware, MiddlewareContext

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
            log.exception(
                f"Error while handling result of {context.request.method_name}"
            )
            context.bridge.send_api_error_response(
                context.request.op_key or "unknown",
                str(e),
                ["method_execution", context.request.method_name],
            )
