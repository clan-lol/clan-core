import json
import logging
import threading
import uuid
from http.server import BaseHTTPRequestHandler
from pathlib import Path
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
        *,
        openapi_file: Path | None = None,
        swagger_dist: Path | None = None,
    ) -> None:
        # Initialize the API bridge fields
        self.api = api
        self.openapi_file = openapi_file
        self.swagger_dist = swagger_dist
        self.middleware_chain = middleware_chain
        self.threads: dict[str, WebThread] = {}

        # Initialize the HTTP handler
        super(BaseHTTPRequestHandler, self).__init__(request, client_address, server)

    def send_api_response(self, response: BackendResponse) -> None:
        """Send HTTP response directly to the client."""

        try:
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
        except BrokenPipeError as e:
            # Handle broken pipe errors gracefully
            log.warning(f"Client disconnected before we could send a response: {e!s}")

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
        elif path.startswith("/api/swagger"):
            if self.swagger_dist and self.swagger_dist.exists():
                # Serve static files from swagger_dist
                rel_path = parsed_url.path[len("/api/swagger") :].lstrip("/")
                # Redirect /api/swagger (no trailing slash or file) to /api/swagger/index.html
                if rel_path == "":
                    self.send_response(302)
                    self.send_header("Location", "/api/swagger/index.html")
                    self.end_headers()
                    return
                file_path = self.swagger_dist / rel_path
                if rel_path == "index.html":
                    file_path = Path(__file__).parent / "swagger.html"
                elif rel_path == "openapi.json":
                    if not self.openapi_file:
                        self.send_error(404, "OpenAPI file not found")
                        return
                    file_path = self.openapi_file

                if file_path.exists() and file_path.is_file():
                    try:
                        # Guess content type
                        if file_path.suffix == ".html":
                            content_type = "text/html"
                        elif file_path.suffix == ".js":
                            content_type = "application/javascript"
                        elif file_path.suffix == ".css":
                            content_type = "text/css"
                        elif file_path.suffix == ".json":
                            content_type = "application/json"
                        elif file_path.suffix == ".png":
                            content_type = "image/png"
                        elif file_path.suffix == ".svg":
                            content_type = "image/svg+xml"
                        else:
                            content_type = "application/octet-stream"
                        with file_path.open("rb") as f:
                            file_data = f.read()
                        if rel_path == "openapi.json":
                            json_data = json.loads(file_data.decode("utf-8"))
                            json_data["servers"] = [
                                {
                                    "url": f"http://{getattr(self.server, 'server_address', ('localhost', 80))[0]}:{getattr(self.server, 'server_address', ('localhost', 80))[1]}/api/v1/"
                                }
                            ]
                            file_data = json.dumps(json_data, indent=2).encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", content_type)
                        self.end_headers()

                        self.wfile.write(file_data)
                    except Exception as e:
                        log.error(f"Error reading Swagger file: {e!s}")
                        self.send_error(500, "Internal Server Error")
                else:
                    self.send_error(404, "Swagger file not found")
            else:
                self.send_error(404, "Swagger file not found")

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

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Check if this is an API call
        if not path.startswith("/api/v1/"):
            self.send_api_error_response(
                "post", f"Path not found  {path}", ["http_bridge", "POST"]
            )
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
        gen_op_key = str(uuid.uuid4())

        # Handle the API request
        try:
            self._handle_api_request(method_name, request_data, gen_op_key)
        except Exception as e:
            log.exception(f"Error processing API request {method_name}")
            self.send_api_error_response(
                gen_op_key,
                f"Internal server error: {e!s}",
                ["http_bridge", "POST", method_name],
            )

    def _handle_api_request(
        self,
        method_name: str,
        request_data: dict[str, Any],
        gen_op_key: str,
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

            op_key = header.get("op_key", gen_op_key)
            if not isinstance(op_key, str):
                msg = f"Expected op_key to be a string, got {type(op_key)}"
                raise TypeError(msg)

            # Check if op_key is a valid UUID
            try:
                uuid.UUID(op_key)
            except ValueError as e:
                msg = f"op_key '{op_key}' is not a valid UUID"
                raise TypeError(msg) from e

            if op_key in self.threads:
                msg = f"Operation key '{op_key}' is already in use. Please try again."
                raise ValueError(msg)

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
