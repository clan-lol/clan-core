import json
import logging
import threading
import uuid
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from clan_lib.api import (
    MethodRegistry,
    SuccessDataClass,
    dataclass_to_dict,
)
from clan_lib.api.tasks import WebThread
from clan_lib.async_run import (
    set_current_thread_opkey,
    set_should_cancel,
)

from clan_app.api.api_bridge import ApiBridge, BackendRequest, BackendResponse

if TYPE_CHECKING:
    from clan_app.middleware.base import Middleware

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
        shared_threads: dict[str, WebThread] | None = None,
    ) -> None:
        # Initialize API bridge fields
        self.api = api
        self.middleware_chain = middleware_chain
        self.threads = shared_threads if shared_threads is not None else {}

        # Initialize OpenAPI/Swagger fields
        self.openapi_file = openapi_file
        self.swagger_dist = swagger_dist

        # Initialize HTTP handler
        super(BaseHTTPRequestHandler, self).__init__(request, client_address, server)

    def _send_cors_headers(self) -> None:
        """Send CORS headers for cross-origin requests."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json_response_with_status(
        self,
        data: dict[str, Any],
        status_code: int = 200,
    ) -> None:
        """Send a JSON response with the given status code."""
        try:
            self.send_response_only(status_code)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()

            response_data = json.dumps(data, indent=2, ensure_ascii=False)
            self.wfile.write(response_data.encode("utf-8"))
        except BrokenPipeError as e:
            log.warning(f"Client disconnected before we could send a response: {e!s}")

    def send_api_response(self, response: BackendResponse) -> None:
        """Send HTTP response directly to the client."""
        response_dict = dataclass_to_dict(response)
        self._send_json_response_with_status(response_dict, 200)
        log.debug(
            f"HTTP response for {response._op_key}: {json.dumps(response_dict, indent=2)}",  # noqa: SLF001
        )

    def _create_success_response(
        self,
        op_key: str,
        data: dict[str, Any],
    ) -> BackendResponse:
        """Create a successful API response."""
        return BackendResponse(
            body=SuccessDataClass(op_key=op_key, status="success", data=data),
            header={},
            _op_key=op_key,
        )

    def _send_info_response(self) -> None:
        """Send server information response."""
        response = self._create_success_response(
            "info",
            {"message": "Clan API Server", "version": "1.0.0"},
        )
        self.send_api_response(response)

    def _send_methods_response(self) -> None:
        """Send available API methods response."""
        response = self._create_success_response(
            "methods",
            {"methods": list(self.api.functions.keys())},
        )
        self.send_api_response(response)

    def _handle_swagger_request(self, parsed_url: Any) -> None:
        """Handle Swagger UI related requests."""
        if not self.swagger_dist or not self.swagger_dist.exists():
            self.send_error(404, "Swagger file not found")
            return

        rel_path = parsed_url.path[len("/api/swagger") :].lstrip("/")

        # Redirect /api/swagger to /api/swagger/index.html
        if rel_path == "":
            self.send_response(302)
            self.send_header("Location", "/api/swagger/index.html")
            self.end_headers()
            return

        self._serve_swagger_file(rel_path)

    def _serve_swagger_file(self, rel_path: str) -> None:
        """Serve a specific Swagger UI file."""
        file_path = self._get_swagger_file_path(rel_path)

        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "Swagger file not found")
            return

        try:
            content_type = self._get_content_type(file_path)
            file_data = self._read_and_process_file(file_path, rel_path)

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(file_data)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            log.exception("Error reading Swagger file")
            self.send_error(500, "Internal Server Error")

    def _get_swagger_file_path(self, rel_path: str) -> Path:
        """Get the file path for a Swagger resource."""
        if rel_path == "index.html":
            return Path(__file__).parent / "swagger.html"
        if rel_path == "openapi.json":
            if not self.openapi_file:
                return Path("/nonexistent")  # Will fail exists() check
            return self.openapi_file
        return (
            self.swagger_dist / rel_path if self.swagger_dist else Path("/nonexistent")
        )

    def _get_content_type(self, file_path: Path) -> str:
        """Get the content type for a file based on its extension."""
        content_types = {
            ".html": "text/html",
            ".js": "application/javascript",
            ".css": "text/css",
            ".json": "application/json",
            ".png": "image/png",
            ".svg": "image/svg+xml",
        }
        return content_types.get(file_path.suffix, "application/octet-stream")

    def _read_and_process_file(self, file_path: Path, rel_path: str) -> bytes:
        """Read and optionally process a file (e.g., inject server URL into openapi.json)."""
        with file_path.open("rb") as f:
            file_data = f.read()

        if rel_path == "openapi.json":
            json_data = json.loads(file_data.decode("utf-8"))
            server_address = getattr(self.server, "server_address", ("localhost", 80))
            json_data["servers"] = [
                {"url": f"http://{server_address[0]}:{server_address[1]}/api/v1/"},
            ]
            file_data = json.dumps(json_data, indent=2).encode("utf-8")

        return file_data

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response_only(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            self._send_info_response()
        elif path.startswith("/api/swagger"):
            self._handle_swagger_request(parsed_url)
        elif path == "/api/methods":
            self._send_methods_response()
        else:
            self.send_api_error_response("info", "Not Found", ["http_bridge", "GET"])

    def do_POST(self) -> None:
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Validate API path
        if not path.startswith("/api/v1/"):
            self.send_api_error_response(
                "post",
                f"Path not found: {path}",
                ["http_bridge", "POST"],
            )
            return

        # Extract and validate method name
        method_name = path[len("/api/v1/") :]
        if not method_name:
            self.send_api_error_response(
                "post",
                "Method name required",
                ["http_bridge", "POST"],
            )
            return

        if method_name not in self.api.functions:
            self.send_api_error_response(
                "post",
                f"Method '{method_name}' not found",
                ["http_bridge", "POST", method_name],
            )
            return

        # Read and parse request body
        request_data = self._read_request_body(method_name)
        if request_data is None:
            return  # Error already sent

        # Generate operation key and handle request
        gen_op_key = str(uuid.uuid4())
        try:
            self._handle_api_request(method_name, request_data, gen_op_key)
        except RuntimeError as e:
            log.exception(f"Error processing API request {method_name}")
            self.send_api_error_response(
                gen_op_key,
                f"Internal server error: {e!s}",
                ["http_bridge", "POST", method_name],
            )

    def _read_request_body(self, method_name: str) -> dict[str, Any] | None:
        """Read and parse the request body. Returns None if there was an error."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                return {}
            body = self.rfile.read(content_length)
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_api_error_response(
                "post",
                "Invalid JSON in request body",
                ["http_bridge", "POST", method_name],
            )
            return None
        except (OSError, ValueError, UnicodeDecodeError) as e:
            self.send_api_error_response(
                "post",
                f"Error reading request: {e!s}",
                ["http_bridge", "POST", method_name],
            )
            return None

    def _handle_api_request(
        self,
        method_name: str,
        request_data: dict[str, Any],
        gen_op_key: str,
    ) -> None:
        """Handle an API request by processing it through middleware."""
        try:
            # Validate and parse request data
            header, body, op_key = self._parse_request_data(request_data, gen_op_key)

            # Validate operation key
            self._validate_operation_key(op_key)

            # Create API request
            api_request = BackendRequest(
                method_name=method_name,
                args=body,
                header=header,
                op_key=op_key,
            )

        except (KeyError, TypeError, ValueError) as e:
            self.send_api_error_response(
                gen_op_key,
                str(e),
                ["http_bridge", method_name],
            )
            return

        self._process_api_request_in_thread(api_request)

    def _parse_request_data(
        self,
        request_data: dict[str, Any],
        gen_op_key: str,
    ) -> tuple[dict[str, Any], dict[str, Any], str]:
        """Parse and validate request data components."""
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

        return header, body, op_key

    def _validate_operation_key(self, op_key: str) -> None:
        """Validate that the operation key is valid and not in use."""
        try:
            uuid.UUID(op_key)
        except ValueError as e:
            msg = f"op_key '{op_key}' is not a valid UUID"
            raise TypeError(msg) from e

        if op_key in self.threads:
            msg = f"Operation key '{op_key}' is already in use. Please try again."
            raise ValueError(msg)

    def process_request_in_thread(
        self,
        request: BackendRequest,
        *,
        thread_name: str = "ApiBridgeThread",
        wait_for_completion: bool = False,
        timeout: float = 60.0 * 60,  # 1 hour default timeout
    ) -> None:
        pass

    def _process_api_request_in_thread(
        self,
        api_request: BackendRequest,
    ) -> None:
        """Process the API request in a separate thread."""
        stop_event = threading.Event()
        request = api_request
        op_key = request.op_key or "unknown"
        set_should_cancel(lambda: stop_event.is_set())
        set_current_thread_opkey(op_key)

        curr_thread = threading.current_thread()
        self.threads[op_key] = WebThread(thread=curr_thread, stop_event=stop_event)

        log.debug(
            f"Processing {request.method_name} with args {request.args} "
            f"and header {request.header}",
        )
        self.process_request(request)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Override default logging to use our logger."""
        log.info(f"{self.address_string()} - {format % args}")
