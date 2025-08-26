"""Tests for HTTP API components."""

import json
import logging
import threading
import time
from urllib.request import Request, urlopen

import pytest
from clan_lib.api import MethodRegistry, tasks
from clan_lib.async_run import is_async_cancelled

from clan_app.api.middleware import (
    ArgumentParsingMiddleware,
    MethodExecutionMiddleware,
)
from clan_app.deps.http.http_server import HttpApiServer

log = logging.getLogger(__name__)


@pytest.fixture
def mock_api() -> MethodRegistry:
    """Create a mock API with test methods."""
    api = MethodRegistry()

    api.register(tasks.delete_task)

    @api.register
    def test_method(message: str) -> dict[str, str]:
        return {"response": f"Hello {message}!"}

    @api.register
    def test_method_with_error() -> dict[str, str]:
        msg = "Test error"
        raise ValueError(msg)

    @api.register
    def run_task_blocking(wtime: int) -> str:
        """A long blocking task that simulates a long-running operation."""
        time.sleep(1)

        for i in range(wtime):
            if is_async_cancelled():
                log.debug("Task was cancelled")
                return "Task was cancelled"
            log.debug(f"Processing {i} for {wtime}")
            time.sleep(1)
        return f"Task completed with wtime: {wtime}"

    return api


@pytest.fixture
def http_bridge(
    mock_api: MethodRegistry,
) -> tuple[MethodRegistry, tuple]:
    """Create HTTP bridge dependencies for testing."""
    middleware_chain = (
        ArgumentParsingMiddleware(api=mock_api),
        MethodExecutionMiddleware(api=mock_api),
    )
    return mock_api, middleware_chain


@pytest.fixture
def http_server(mock_api: MethodRegistry) -> HttpApiServer:
    """Create HTTP server with mock dependencies."""
    server = HttpApiServer(
        api=mock_api,
        host="127.0.0.1",
        port=8081,  # Use different port for tests
    )

    # Add middleware
    server.add_middleware(ArgumentParsingMiddleware(api=mock_api))
    server.add_middleware(MethodExecutionMiddleware(api=mock_api))

    # Bridge will be created automatically when accessed

    return server


class TestHttpBridge:
    """Tests for HttpBridge class."""

    def test_http_bridge_initialization(self, http_bridge: tuple) -> None:
        """Test HTTP bridge initialization."""
        # Since HttpBridge is now a request handler, we can't instantiate it directly
        # We'll test initialization through the server
        api, middleware_chain = http_bridge
        assert api is not None
        assert len(middleware_chain) == 2

    def test_http_bridge_middleware_setup(self, http_bridge: tuple) -> None:
        """Test that middleware is properly set up."""
        api, middleware_chain = http_bridge

        # Test that we can create the bridge with middleware
        # The actual HTTP handling will be tested through the server integration tests
        assert len(middleware_chain) == 2
        assert isinstance(middleware_chain[0], ArgumentParsingMiddleware)
        assert isinstance(middleware_chain[1], MethodExecutionMiddleware)


class TestHttpApiServer:
    """Tests for HttpApiServer class."""

    def test_server_initialization(self, http_server: HttpApiServer) -> None:
        """Test HTTP server initialization."""
        assert http_server.host == "127.0.0.1"
        assert http_server.port == 8081
        assert http_server.server is None
        assert http_server.server_thread is None
        assert not http_server.is_running()

    def test_server_start_stop(self, http_server: HttpApiServer) -> None:
        """Test starting and stopping the server."""
        # Start server
        http_server.start()
        time.sleep(0.1)  # Give server time to start

        assert http_server.is_running()

        # Stop server
        http_server.stop()
        time.sleep(0.1)  # Give server time to stop

        assert not http_server.is_running()

    def test_server_endpoints(self, http_server: HttpApiServer) -> None:
        """Test server endpoints."""
        # Start server
        http_server.start()
        time.sleep(0.1)  # Give server time to start

        try:
            # Test root endpoint
            response = urlopen("http://127.0.0.1:8081/")
            data: dict = json.loads(response.read().decode())
            assert data["body"]["status"] == "success"
            assert data["body"]["data"]["message"] == "Clan API Server"
            assert data["body"]["data"]["version"] == "1.0.0"

            # Test methods endpoint
            response = urlopen("http://127.0.0.1:8081/api/methods")
            data = json.loads(response.read().decode())
            assert data["body"]["status"] == "success"
            assert "test_method" in data["body"]["data"]["methods"]
            assert "test_method_with_error" in data["body"]["data"]["methods"]

            # Test API call endpoint
            request_data: dict = {"header": {}, "body": {"message": "World"}}
            req: Request = Request(
                "http://127.0.0.1:8081/api/v1/test_method",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )
            response = urlopen(req)  # noqa: S310
            data = json.loads(response.read().decode())

            # Response should be BackendResponse format
            assert "body" in data
            assert "header" in data

            assert data["body"]["status"] == "success"
            assert data["body"]["data"] == {"response": "Hello World!"}

        finally:
            # Always stop server
            http_server.stop()

    def test_server_error_handling(self, http_server: HttpApiServer) -> None:
        """Test server error handling."""
        # Start server
        http_server.start()
        time.sleep(0.1)  # Give server time to start

        try:
            # Test 404 error

            res = urlopen("http://127.0.0.1:8081/nonexistent")
            assert res.status == 200
            body = json.loads(res.read().decode())["body"]
            assert body["status"] == "error"

            # Test method not found
            request_data: dict = {"header": {}, "body": {}}
            req: Request = Request(
                "http://127.0.0.1:8081/api/v1/nonexistent_method",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )

            res = urlopen(req)  # noqa: S310
            assert res.status == 200
            body = json.loads(res.read().decode())["body"]
            assert body["status"] == "error"

            # Test invalid JSON
            req = Request(
                "http://127.0.0.1:8081/api/v1/test_method",
                data=b"invalid json",
                headers={"Content-Type": "application/json"},
            )

            res = urlopen(req)  # noqa: S310
            assert res.status == 200
            body = json.loads(res.read().decode())["body"]
            assert body["status"] == "error"
        finally:
            # Always stop server
            http_server.stop()

    def test_server_cors_headers(self, http_server: HttpApiServer) -> None:
        """Test CORS headers are properly set."""
        # Start server
        http_server.start()
        time.sleep(0.1)  # Give server time to start

        try:
            # Test OPTIONS request
            class OptionsRequest(Request):
                def get_method(self) -> str:
                    return "OPTIONS"

            req: Request = OptionsRequest("http://127.0.0.1:8081/api/call/test_method")
            response = urlopen(req)  # noqa: S310

            # Check CORS headers
            headers = response.info()
            assert headers.get("Access-Control-Allow-Origin") == "*"
            assert "GET" in headers.get("Access-Control-Allow-Methods", "")
            assert "POST" in headers.get("Access-Control-Allow-Methods", "")

        finally:
            # Always stop server
            http_server.stop()


class TestIntegration:
    """Integration tests for HTTP API components."""

    def test_full_request_flow(
        self,
        mock_api: MethodRegistry,
    ) -> None:
        """Test complete request flow from server to bridge to middleware."""
        server: HttpApiServer = HttpApiServer(
            api=mock_api,
            host="127.0.0.1",
            port=8082,
        )

        # Add middleware
        server.add_middleware(ArgumentParsingMiddleware(api=mock_api))
        server.add_middleware(MethodExecutionMiddleware(api=mock_api))

        # Bridge will be created automatically when accessed

        # Start server
        server.start()
        time.sleep(0.1)  # Give server time to start

        try:
            # Make API call
            request_data: dict = {
                "header": {"logging": {"group_path": ["test", "group"]}},
                "body": {"message": "Integration"},
            }
            req: Request = Request(
                "http://127.0.0.1:8082/api/v1/test_method",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )
            response = urlopen(req)  # noqa: S310
            data: dict = json.loads(response.read().decode())

            # Verify response in BackendResponse format
            assert "body" in data
            assert "header" in data
            assert data["body"]["status"] == "success"
            assert data["body"]["data"] == {"response": "Hello Integration!"}

        finally:
            # Always stop server
            server.stop()

    def test_blocking_task(
        self,
        mock_api: MethodRegistry,
    ) -> None:
        shared_threads: dict[str, tasks.WebThread] = {}
        tasks.BAKEND_THREADS = shared_threads

        """Test a long-running blocking task."""
        server: HttpApiServer = HttpApiServer(
            api=mock_api,
            host="127.0.0.1",
            port=8083,
            shared_threads=shared_threads,
        )

        # Add middleware
        server.add_middleware(ArgumentParsingMiddleware(api=mock_api))
        server.add_middleware(MethodExecutionMiddleware(api=mock_api))

        # Start server
        server.start()
        time.sleep(0.1)  # Give server time to start

        blocking_op_key = "b37f920f-ce8c-4c8d-b595-28ca983d265e"  # str(uuid.uuid4())

        def parallel_task() -> None:
            # Make API call
            request_data: dict = {
                "body": {"wtime": 60},
                "header": {"op_key": blocking_op_key},
            }
            req: Request = Request(
                "http://127.0.0.1:8083/api/v1/run_task_blocking",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )
            response = urlopen(req)  # noqa: S310
            data: dict = json.loads(response.read().decode())

            # thread.join()
            assert "body" in data
            assert data["body"]["status"] == "success"
            assert data["body"]["data"] == "Task was cancelled"

        thread = threading.Thread(
            target=parallel_task,
            name="ParallelTaskThread",
            daemon=True,
        )
        thread.start()

        time.sleep(1)
        request_data: dict = {
            "body": {"task_id": blocking_op_key},
        }
        req: Request = Request(
            "http://127.0.0.1:8083/api/v1/delete_task",
            data=json.dumps(request_data).encode(),
            headers={"Content-Type": "application/json"},
        )
        response = urlopen(req)  # noqa: S310
        data: dict = json.loads(response.read().decode())

        assert "body" in data
        assert "header" in data
        assert data["body"]["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
