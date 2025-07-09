"""Tests for HTTP API components."""

import json
import threading
import time
from unittest.mock import Mock
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from clan_lib.api import MethodRegistry
from clan_lib.log_manager import LogManager

from clan_app.api.api_bridge import BackendResponse
from clan_app.api.middleware import (
    ArgumentParsingMiddleware,
    LoggingMiddleware,
    MethodExecutionMiddleware,
)
from clan_app.deps.http.http_bridge import HttpBridge
from clan_app.deps.http.http_server import HttpApiServer


@pytest.fixture
def mock_api() -> MethodRegistry:
    """Create a mock API with test methods."""
    api = MethodRegistry()

    @api.register
    def test_method(message: str) -> dict[str, str]:
        return {"response": f"Hello {message}!"}

    @api.register
    def test_method_with_error() -> dict[str, str]:
        msg = "Test error"
        raise ValueError(msg)

    return api


@pytest.fixture
def mock_log_manager() -> Mock:
    """Create a mock log manager."""
    log_manager = Mock(spec=LogManager)
    log_manager.create_log_file.return_value.get_file_path.return_value = Mock()
    log_manager.create_log_file.return_value.get_file_path.return_value.open.return_value = Mock()
    return log_manager


@pytest.fixture
def http_bridge(mock_api: MethodRegistry, mock_log_manager: Mock) -> HttpBridge:
    """Create HTTP bridge with mock dependencies."""
    return HttpBridge(
        middleware_chain=(
            ArgumentParsingMiddleware(api=mock_api),
            LoggingMiddleware(log_manager=mock_log_manager),
            MethodExecutionMiddleware(api=mock_api),
        )
    )


@pytest.fixture
def http_server(mock_api: MethodRegistry, mock_log_manager: Mock) -> HttpApiServer:
    """Create HTTP server with mock dependencies."""
    return HttpApiServer(
        api=mock_api,
        log_manager=mock_log_manager,
        host="127.0.0.1",
        port=8081,  # Use different port for tests
    )


class TestHttpBridge:
    """Tests for HttpBridge class."""

    def test_http_bridge_initialization(self, http_bridge: HttpBridge) -> None:
        """Test HTTP bridge initialization."""
        assert http_bridge.threads == {}
        assert http_bridge.response_handler is None

    def test_set_response_handler(self, http_bridge: HttpBridge) -> None:
        """Test setting response handler."""
        handler: Mock = Mock()
        http_bridge.set_response_handler(handler)
        assert http_bridge.response_handler == handler

    def test_handle_http_request_success(self, http_bridge: HttpBridge) -> None:
        """Test successful HTTP request handling."""
        # Set up response handler
        response_received: threading.Event = threading.Event()
        received_response: dict = {}

        def response_handler(response: BackendResponse) -> None:
            received_response["response"] = response
            response_received.set()

        http_bridge.set_response_handler(response_handler)

        # Make request
        request_data: dict = {"header": {}, "body": {"message": "World"}}

        http_bridge.handle_http_request("test_method", request_data, "test-op-key")

        # Wait for response
        assert response_received.wait(timeout=5)
        response = received_response["response"]

        assert response._op_key == "test-op-key"  # noqa: SLF001
        assert response.body.data == {"response": "Hello World!"}

    def test_handle_http_request_with_invalid_header(
        self, http_bridge: HttpBridge
    ) -> None:
        """Test HTTP request with invalid header."""
        response_received: threading.Event = threading.Event()
        received_response: dict = {}

        def response_handler(response: BackendResponse) -> None:
            received_response["response"] = response
            response_received.set()

        http_bridge.set_response_handler(response_handler)

        # Make request with invalid header
        request_data: dict = {
            "header": "invalid_header",  # Should be dict
            "body": {"message": "World"},
        }

        http_bridge.handle_http_request("test_method", request_data, "test-op-key")

        # Wait for response
        assert response_received.wait(timeout=5)
        response = received_response["response"]

        assert response._op_key == "test-op-key"  # noqa: SLF001
        assert response.body.status == "error"


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
            assert data["message"] == "Clan API Server"
            assert data["version"] == "1.0.0"

            # Test methods endpoint
            response = urlopen("http://127.0.0.1:8081/api/methods")
            data = json.loads(response.read().decode())
            assert "test_method" in data["methods"]
            assert "test_method_with_error" in data["methods"]

            # Test API call endpoint
            request_data: dict = {"header": {}, "body": {"message": "World"}}
            req: Request = Request(
                "http://127.0.0.1:8081/api/call/test_method",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )
            response = urlopen(req)
            data = json.loads(response.read().decode())

            assert data["success"] is True
            assert data["data"]["data"] == {"response": "Hello World!"}

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
            with pytest.raises(HTTPError) as exc_info:
                urlopen("http://127.0.0.1:8081/nonexistent")
            assert exc_info.value.code == 404

            # Test method not found
            request_data: dict = {"header": {}, "body": {}}
            req: Request = Request(
                "http://127.0.0.1:8081/api/call/nonexistent_method",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )
            with pytest.raises(HTTPError) as exc_info:
                urlopen(req)
            assert exc_info.value.code == 404

            # Test invalid JSON
            req = Request(
                "http://127.0.0.1:8081/api/call/test_method",
                data=b"invalid json",
                headers={"Content-Type": "application/json"},
            )
            with pytest.raises(HTTPError) as exc_info:
                urlopen(req)
            assert exc_info.value.code == 400

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
            response = urlopen(req)

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
        self, mock_api: MethodRegistry, mock_log_manager: Mock
    ) -> None:
        """Test complete request flow from server to bridge to middleware."""
        server: HttpApiServer = HttpApiServer(
            api=mock_api,
            log_manager=mock_log_manager,
            host="127.0.0.1",
            port=8082,
        )

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
                "http://127.0.0.1:8082/api/call/test_method",
                data=json.dumps(request_data).encode(),
                headers={"Content-Type": "application/json"},
            )
            response = urlopen(req)
            data: dict = json.loads(response.read().decode())

            # Verify response
            assert data["success"] is True
            assert data["data"]["data"] == {"response": "Hello Integration!"}
            assert "op_key" in data

        finally:
            # Always stop server
            server.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
