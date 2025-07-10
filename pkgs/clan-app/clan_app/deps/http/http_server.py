import logging
import threading
from http.server import HTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Any

from clan_lib.api import MethodRegistry
from clan_lib.api.tasks import WebThread

if TYPE_CHECKING:
    from clan_app.api.middleware import Middleware

from .http_bridge import HttpBridge

log = logging.getLogger(__name__)


class HttpApiServer:
    """HTTP server for the Clan API using Python's built-in HTTP server."""

    def __init__(
        self,
        api: MethodRegistry,
        host: str = "127.0.0.1",
        port: int = 8080,
        openapi_file: Path | None = None,
        swagger_dist: Path | None = None,
        shared_threads: dict[str, WebThread] | None = None,
    ) -> None:
        self.api = api
        self.openapi = openapi_file
        self.swagger_dist = swagger_dist
        self.host = host
        self.port = port
        self._server: HTTPServer | None = None
        self._server_thread: threading.Thread | None = None
        # Bridge is now the request handler itself, no separate instance needed
        self._middleware: list[Middleware] = []
        self.shared_threads = shared_threads or {}

    def add_middleware(self, middleware: "Middleware") -> None:
        """Add middleware to the middleware chain."""
        if self._server is not None:
            msg = "Cannot add middleware after server is started"
            raise RuntimeError(msg)
        self._middleware.append(middleware)

    @property
    def server(self) -> HTTPServer | None:
        """Get the HTTP server instance."""
        return self._server

    @property
    def server_thread(self) -> threading.Thread | None:
        """Get the server thread."""
        return self._server_thread

    def _create_request_handler(self) -> type[HttpBridge]:
        """Create a request handler class with injected dependencies."""
        api = self.api
        middleware_chain = tuple(self._middleware)
        openapi_file = self.openapi
        swagger_dist = self.swagger_dist
        shared_threads = self.shared_threads

        class RequestHandler(HttpBridge):
            def __init__(self, request: Any, client_address: Any, server: Any) -> None:
                super().__init__(
                    api=api,
                    middleware_chain=middleware_chain,
                    request=request,
                    client_address=client_address,
                    server=server,
                    openapi_file=openapi_file,
                    swagger_dist=swagger_dist,
                    shared_threads=shared_threads,
                )

        return RequestHandler

    def start(self) -> None:
        """Start the HTTP server in a separate thread."""
        if self._server_thread is not None:
            log.warning("HTTP server is already running")
            return

        # Create the server
        handler_class = self._create_request_handler()
        self._server = HTTPServer((self.host, self.port), handler_class)

        def run_server() -> None:
            if self._server:
                log.info(f"HTTP API server started on http://{self.host}:{self.port}")
                self._server.serve_forever()

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

    def stop(self) -> None:
        """Stop the HTTP server."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

        if self._server_thread:
            self._server_thread.join(timeout=5)
            self._server_thread = None

        log.info("HTTP API server stopped")

    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._server_thread is not None and self._server_thread.is_alive()
