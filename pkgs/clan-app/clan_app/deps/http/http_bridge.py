import json
import logging
import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from clan_lib.api import dataclass_to_dict
from clan_lib.api.tasks import WebThread
from clan_lib.async_run import set_should_cancel

from clan_app.api.api_bridge import ApiBridge, BackendRequest, BackendResponse

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)


@dataclass
class HttpBridge(ApiBridge):
    """HTTP-specific implementation of the API bridge."""

    threads: dict[str, WebThread] = field(default_factory=dict)
    response_handler: "Callable[[BackendResponse], None] | None" = None

    def send_response(self, response: BackendResponse) -> None:
        """Send response back to the HTTP client."""
        if self.response_handler:
            self.response_handler(response)
        else:
            # Default behavior - just log the response
            serialized = json.dumps(
                dataclass_to_dict(response), indent=4, ensure_ascii=False
            )
            log.debug(f"HTTP response: {serialized}")

    def handle_http_request(
        self,
        method_name: str,
        request_data: dict[str, Any],
        op_key: str,
    ) -> None:
        """Handle an HTTP API request."""
        try:
            # Parse the HTTP request format
            header = request_data.get("header", {})
            if not isinstance(header, dict):
                msg = f"Expected header to be a dict, got {type(header)}"
                raise TypeError(msg)

            body = request_data.get("body", {})
            if not isinstance(body, dict):
                msg = f"Expected body to be a dict, got {type(body)}"
                raise TypeError(msg)

            # Create API request
            api_request = BackendRequest(
                method_name=method_name, args=body, header=header, op_key=op_key
            )

        except Exception as e:
            self.send_error_response(op_key, str(e), ["http_bridge", method_name])
            return

        # Process in a separate thread
        def thread_task(stop_event: threading.Event) -> None:
            set_should_cancel(lambda: stop_event.is_set())

            try:
                self.process_request(api_request)
            finally:
                self.threads.pop(op_key, None)

        stop_event = threading.Event()
        thread = threading.Thread(
            target=thread_task, args=(stop_event,), name="HttpThread"
        )
        thread.start()
        self.threads[op_key] = WebThread(thread=thread, stop_event=stop_event)

    def set_response_handler(
        self, handler: "Callable[[BackendResponse], None]"
    ) -> None:
        """Set a custom response handler for HTTP responses."""
        self.response_handler = handler
