import json
import logging
import threading
import uuid
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from clan_lib.api import MethodRegistry, SuccessDataClass, dataclass_to_dict
from clan_lib.api.tasks import WebThread
from clan_lib.async_run import set_should_cancel

from clan_app.api.api_bridge import ApiBridge, BackendRequest, BackendResponse

if TYPE_CHECKING:
    from clan_app.api.middleware import Middleware

log = logging.getLogger(__name__)


class HttpBridge(ApiBridge, BaseHTTPRequestHandler):
    """HTTP-specific implementation of the API bridge that handles HTTP requests directly.

    This bridge combines the API bridge functionality with HTTP request handling.
    """

    def __init__(
        self,
        api: MethodRegistry,
        middleware_chain: tuple["Middleware", ...],
        request: Any,
        client_address: Any,
        server: Any,
    ) -> None:
        # Initialize the API bridge fields
        self.api = api
        self.middleware_chain = middleware_chain
        self.threads: dict[str, WebThread] = {}
        self._current_response: BackendResponse | None = None

        # Initialize the HTTP handler
        super(BaseHTTPRequestHandler, self).__init__(request, client_address, server)

    def send_api_response(self, response: BackendResponse) -> None:
        """Send HTTP response directly to the client."""
        self._current_response = response

        # Send HTTP response
        self.send_response_only(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        # Write response data
        response_data = json.dumps(
            dataclass_to_dict(response), indent=2, ensure_ascii=False
        )
        self.wfile.write(response_data.encode("utf-8"))

        # Log the response for debugging
        log.debug(f"HTTP response for {response._op_key}: {response_data}")  # noqa: SLF001

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle CORS preflight requests."""
        self.send_response_only(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            response = BackendResponse(
                body=SuccessDataClass(
                    op_key="info",
                    status="success",
                    data={"message": "Clan API Server", "version": "1.0.0"},
                ),
                header={},
                _op_key="info",
            )
            self.send_api_response(response)
        elif path == "/api/methods":
            response = BackendResponse(
                body=SuccessDataClass(
                    op_key="methods",
                    status="success",
                    data={"methods": list(self.api.functions.keys())},
                ),
                header={},
                _op_key="methods",
            )
            self.send_api_response(response)
        else:
            self.send_api_error_response("info", "Not Found", ["http_bridge", "GET"])

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Check if this is an API call
        if not path.startswith("/api/v1/"):
            self.send_api_error_response("post", "Not Found", ["http_bridge", "POST"])
            return

        # Extract method name from path
        method_name = path[len("/api/v1/") :]

        if not method_name:
            self.send_api_error_response(
                "post", "Method name required", ["http_bridge", "POST"]
            )
            return

        if method_name not in self.api.functions:
            self.send_api_error_response(
                "post",
                f"Method '{method_name}' not found",
                ["http_bridge", "POST", method_name],
            )
            return

        # Read request body
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                request_data = json.loads(body.decode("utf-8"))
            else:
                request_data = {}
        except json.JSONDecodeError:
            self.send_api_error_response(
                "post",
                "Invalid JSON in request body",
                ["http_bridge", "POST", method_name],
            )
            return
        except Exception as e:
            self.send_api_error_response(
                "post",
                f"Error reading request: {e!s}",
                ["http_bridge", "POST", method_name],
            )
            return

        # Generate a unique operation key
        op_key = str(uuid.uuid4())

        # Handle the API request
        try:
            self._handle_api_request(method_name, request_data, op_key)
        except Exception as e:
            log.exception(f"Error processing API request {method_name}")
            self.send_api_error_response(
                op_key,
                f"Internal server error: {e!s}",
                ["http_bridge", "POST", method_name],
            )

    def _handle_api_request(
        self,
        method_name: str,
        request_data: dict[str, Any],
        op_key: str,
    ) -> None:
        """Handle an API request by processing it through middleware."""
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
            # Create error response directly
            self.send_api_error_response(op_key, str(e), ["http_bridge", method_name])
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

        # Wait for the thread to complete (this blocks until response is sent)
        thread.join(timeout=60.0)

        # If thread is still alive, it timed out
        if thread.is_alive():
            stop_event.set()  # Cancel the thread
            self.send_api_error_response(
                op_key, "Request timeout", ["http_bridge", method_name]
            )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Override default logging to use our logger."""
        log.info(f"{self.address_string()} - {format % args}")
