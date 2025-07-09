import json
import logging
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

from clan_lib.api import MethodRegistry, dataclass_to_dict
from clan_lib.log_manager import LogManager

from clan_app.api.api_bridge import BackendResponse
from clan_app.api.middleware import (
    ArgumentParsingMiddleware,
    LoggingMiddleware,
    MethodExecutionMiddleware,
)

from .http_bridge import HttpBridge

log = logging.getLogger(__name__)


class ClanAPIRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Clan API."""

    def __init__(
        self, *args: Any, api: MethodRegistry, bridge: HttpBridge, **kwargs: Any
    ) -> None:
        self.api = api
        self.bridge = bridge
        super().__init__(*args, **kwargs)

    def _send_json_response(self, data: dict[str, Any], status_code: int = 200) -> None:
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        response_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(response_data.encode("utf-8"))

    def _send_error_response(self, message: str, status_code: int = 400) -> None:
        """Send an error response."""
        self._send_json_response(
            {
                "success": False,
                "error": message,
                "status_code": status_code,
            },
            status_code=status_code,
        )

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            self._send_json_response(
                {
                    "message": "Clan API Server",
                    "version": "1.0.0",
                }
            )
        elif path == "/api/methods":
            self._send_json_response({"methods": list(self.api.functions.keys())})
        else:
            self._send_error_response("Not Found", 404)

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Check if this is an API call
        if not path.startswith("/api/call/"):
            self._send_error_response("Not Found", 404)
            return

        # Extract method name from path
        method_name = path[len("/api/call/") :]

        if not method_name:
            self._send_error_response("Method name required", 400)
            return

        if method_name not in self.api.functions:
            self._send_error_response(f"Method '{method_name}' not found", 404)
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
            self._send_error_response("Invalid JSON in request body", 400)
            return
        except Exception as e:
            self._send_error_response(f"Error reading request: {e!s}", 400)
            return

        # Generate a unique operation key
        op_key = str(uuid.uuid4())

        # Store the response for this request
        response_data: dict[str, Any] = {}
        response_event = threading.Event()

        def response_handler(response: BackendResponse) -> None:
            response_data["response"] = response
            response_event.set()

        # Set the response handler
        self.bridge.set_response_handler(response_handler)

        # Process the request
        self.bridge.handle_http_request(method_name, request_data, op_key)

        # Wait for the response (with timeout)
        if not response_event.wait(timeout=60):  # 60 second timeout
            self._send_error_response("Request timeout", 408)
            return

        # Get the response
        response = response_data["response"]

        # Convert to JSON-serializable format
        if response.body is not None:
            response_dict = dataclass_to_dict(response)
        else:
            response_dict = None

        self._send_json_response(
            response_dict if response_dict is not None else {},
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Override default logging to use our logger."""
        log.info(f"{self.address_string()} - {format % args}")


class HttpApiServer:
    """HTTP server for the Clan API using Python's built-in HTTP server."""

    def __init__(
        self,
        api: MethodRegistry,
        log_manager: LogManager,
        host: str = "127.0.0.1",
        port: int = 8080,
    ) -> None:
        self.api = api
        self.log_manager = log_manager
        self.host = host
        self.port = port
        self.server: HTTPServer | None = None
        self.server_thread: threading.Thread | None = None
        self.bridge = self._create_bridge()

    def _create_bridge(self) -> HttpBridge:
        """Create HTTP bridge with middleware."""
        return HttpBridge(
            middleware_chain=(
                ArgumentParsingMiddleware(api=self.api),
                LoggingMiddleware(log_manager=self.log_manager),
                MethodExecutionMiddleware(api=self.api),
            )
        )

    def _create_request_handler(self) -> type[ClanAPIRequestHandler]:
        """Create a request handler class with injected dependencies."""
        api = self.api
        bridge = self.bridge

        class RequestHandler(ClanAPIRequestHandler):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, api=api, bridge=bridge, **kwargs)

        return RequestHandler

    def start(self) -> None:
        """Start the HTTP server in a separate thread."""
        if self.server_thread is not None:
            log.warning("HTTP server is already running")
            return

        # Create the server
        handler_class = self._create_request_handler()
        self.server = HTTPServer((self.host, self.port), handler_class)

        def run_server() -> None:
            if self.server:
                self.server.serve_forever()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def stop(self) -> None:
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

        if self.server_thread:
            self.server_thread.join(timeout=5)
            self.server_thread = None

        log.info("HTTP API server stopped")

    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.server_thread is not None and self.server_thread.is_alive()
