import logging
import threading
from abc import ABC, abstractmethod
from contextlib import ExitStack
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from clan_lib.api import ApiResponse
from clan_lib.api.tasks import WebThread
from clan_lib.async_run import set_should_cancel

if TYPE_CHECKING:
    from .middleware import Middleware

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackendRequest:
    method_name: str
    args: dict[str, Any]
    header: dict[str, Any]
    op_key: str | None


@dataclass(frozen=True)
class BackendResponse:
    body: ApiResponse
    header: dict[str, Any]
    _op_key: str


@dataclass
class ApiBridge(ABC):
    """Generic interface for API bridges that can handle method calls from different sources."""

    middleware_chain: tuple["Middleware", ...]
    threads: dict[str, WebThread] = field(default_factory=dict)

    @abstractmethod
    def send_api_response(self, response: BackendResponse) -> None:
        """Send response back to the client."""

    def process_request(self, request: BackendRequest) -> None:
        """Process an API request through the middleware chain."""
        from .middleware import MiddlewareContext

        with ExitStack() as stack:
            context = MiddlewareContext(
                request=request,
                bridge=self,
                exit_stack=stack,
            )

            # Process through middleware chain
            for middleware in self.middleware_chain:
                try:
                    log.debug(
                        f"{middleware.__class__.__name__} => {request.method_name}"
                    )
                    middleware.process(context)
                except Exception as e:
                    # If middleware fails, handle error
                    self.send_api_error_response(
                        request.op_key or "unknown", str(e), ["middleware_error"]
                    )
                    return

    def send_api_error_response(
        self, op_key: str, error_message: str, location: list[str]
    ) -> None:
        """Send an error response."""
        from clan_lib.api import ApiError, ErrorDataClass

        error_data = ErrorDataClass(
            op_key=op_key,
            status="error",
            errors=[
                ApiError(
                    message="An internal error occured",
                    description=error_message,
                    location=location,
                )
            ],
        )

        response = BackendResponse(
            body=error_data,
            header={},
            _op_key=op_key,
        )

        self.send_api_response(response)

    def process_request_in_thread(
        self,
        request: BackendRequest,
        *,
        thread_name: str = "ApiBridgeThread",
        wait_for_completion: bool = False,
        timeout: float = 60.0,
    ) -> None:
        """Process an API request in a separate thread with cancellation support.

        Args:
            request: The API request to process
            thread_name: Name for the thread (for debugging)
            wait_for_completion: Whether to wait for the thread to complete
            timeout: Timeout in seconds when waiting for completion
        """
        op_key = request.op_key or "unknown"

        def thread_task(stop_event: threading.Event) -> None:
            set_should_cancel(lambda: stop_event.is_set())
            try:
                log.debug(
                    f"Processing {request.method_name} with args {request.args} "
                    f"and header {request.header} in thread {thread_name}"
                )
                self.process_request(request)
            finally:
                self.threads.pop(op_key, None)

        stop_event = threading.Event()
        thread = threading.Thread(
            target=thread_task, args=(stop_event,), name=thread_name
        )
        thread.start()

        self.threads[op_key] = WebThread(thread=thread, stop_event=stop_event)

        if wait_for_completion:
            # Wait for the thread to complete (this blocks until response is sent)
            thread.join(timeout=timeout)

            # Handle timeout
            if thread.is_alive():
                stop_event.set()  # Cancel the thread
                self.send_api_error_response(
                    op_key, "Request timeout", ["api_bridge", request.method_name]
                )
