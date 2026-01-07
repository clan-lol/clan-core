import functools
import json
import logging
import platform
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from time import sleep
from typing import TYPE_CHECKING, Any

from clan_lib.api import MethodRegistry, message_queue
from clan_lib.api.tasks import WebThread

from ._webview_ffi import (
    _encode_c_string,
    _webview_lib,
)
from .webview_bridge import WebviewBridge

# Default URL patterns to allow (local URLs only)
DEFAULT_URL_PATTERNS: list[str] = [
    r"^file://.*$",
    r"^blob:.*$",
    r"^data:.*$",
    r"^about:.*$",
    r"^http://localhost(:[0-9]+)?(/.*)?$",
    r"^http://127\.0\.0\.1(:[0-9]+)?(/.*)?$",
    r"^http://\[::1\](:[0-9]+)?(/.*)?$",
    r"^https://localhost(:[0-9]+)?(/.*)?$",
    r"^https://127\.0\.0\.1(:[0-9]+)?(/.*)?$",
    r"^https://\[::1\](:[0-9]+)?(/.*)?$",
]

if TYPE_CHECKING:
    from clan_app.middleware.base import Middleware

log = logging.getLogger(__name__)


class SizeHint(IntEnum):
    NONE = 0
    MIN = 1
    MAX = 2
    FIXED = 3


class FuncStatus(IntEnum):
    SUCCESS = 0
    FAILURE = 1


class NativeHandleKind(IntEnum):
    # Top-level window. @c GtkWindow pointer (GTK), @c NSWindow pointer (Cocoa)
    # or @c HWND (Win32)
    UI_WINDOW = 0

    # Browser widget. @c GtkWidget pointer (GTK), @c NSView pointer (Cocoa) or
    # @c HWND (Win32).
    UI_WIDGET = 1

    # Browser controller. @c WebKitWebView pointer (WebKitGTK), @c WKWebView
    # pointer (Cocoa/WebKit) or @c ICoreWebView2Controller pointer
    # (Win32/WebView2).
    BROWSER_CONTROLLER = 2


@dataclass(frozen=True)
class Size:
    width: int
    height: int
    hint: SizeHint


@dataclass
class Webview:
    title: str
    debug: bool = False
    size: Size | None = None
    window: int | None = None
    shared_threads: dict[str, WebThread] | None = None
    app_id: str | None = None
    url_patterns: list[str] = field(default_factory=lambda: DEFAULT_URL_PATTERNS.copy())
    url_blocked_callback: Callable[[str], None] | None = None

    # initialized later
    _bridge: WebviewBridge | None = None
    _handle: Any | None = None
    __callbacks: dict[str, Callable[..., Any]] = field(default_factory=dict)
    _middleware: list["Middleware"] = field(default_factory=list)
    _url_blocked_callback: Any | None = None  # prevent GC of C callback

    @property
    def callbacks(self) -> dict[str, Callable[..., Any]]:
        return self.__callbacks

    @callbacks.setter
    def callbacks(self, value: dict[str, Callable[..., Any]]) -> None:
        del value  # Unused
        msg = "Cannot set callbacks directly"
        raise AttributeError(msg)

    def delete_callback(self, name: str) -> None:
        if name in self.callbacks:
            del self.__callbacks[name]
        else:
            msg = f"Callback {name} does not exist. Cannot delete."
            raise RuntimeError(msg)

    def add_callback(self, name: str, callback: Callable[..., Any]) -> None:
        if name in self.callbacks:
            msg = f"Callback {name} already exists. Cannot add."
            raise RuntimeError(msg)
        self.__callbacks[name] = callback

    def _create_handle(self) -> None:
        # Initialize the webview handle
        with_debugger = True

        # Use webview_create_with_app_id only on Linux if app_id is provided
        if self.app_id and platform.system() == "Linux":
            handle = _webview_lib.webview_create_with_app_id(
                int(with_debugger), self.window, _encode_c_string(self.app_id)
            )
        else:
            handle = _webview_lib.webview_create(int(with_debugger), self.window)

        # Since we can't use object.__setattr__, we'll initialize differently
        # by storing in __dict__ directly (this works for init=False fields)
        self._handle = handle

        # Configure URL allowlist
        for pattern in self.url_patterns:
            self.add_url_pattern(pattern)

        if self.url_blocked_callback:
            self.set_url_blocked_callback(self.url_blocked_callback)

        if self.title:
            self.set_title(self.title)

        if self.size:
            self.set_size(self.size)

    def __post_init__(self) -> None:
        self.setup_notify()  # Start the notification loop

    def setup_notify(self) -> None:
        def loop() -> None:
            while True:
                try:
                    msg = message_queue.get()  # Blocks until available
                    js_code = f"window.notifyBus({json.dumps(msg)});"
                    self.eval(js_code)
                except (json.JSONDecodeError, RuntimeError, AttributeError) as e:
                    print("Bridge notify error:", e)
                sleep(0.01)  # avoid busy loop

        threading.Thread(target=loop, daemon=True).start()

    @property
    def handle(self) -> Any:
        """Get the webview handle, creating it if necessary."""
        if self._handle is None:
            self._create_handle()
        return self._handle

    @property
    def bridge(self) -> "WebviewBridge":
        """Get the bridge, creating it if necessary."""
        if self._bridge is None:
            self.create_bridge()
        if self._bridge is None:
            msg = "Bridge should be created"
            raise RuntimeError(msg)
        return self._bridge

    def api_wrapper(
        self,
        method_name: str,
        op_key_bytes: bytes,
        request_data: bytes,
        arg: int,
    ) -> None:
        """Legacy API wrapper - delegates to the bridge."""
        del arg  # Unused but required for C callback signature
        self.bridge.handle_webview_call(
            method_name=method_name,
            op_key_bytes=op_key_bytes,
            request_data=request_data,
        )

    @property
    def threads(self) -> dict[str, WebThread]:
        """Access threads from the bridge for compatibility."""
        return self.bridge.threads

    def add_middleware(self, middleware: "Middleware") -> None:
        """Add middleware to the middleware chain."""
        if self._bridge is not None:
            msg = "Cannot add middleware after bridge creation."
            raise RuntimeError(msg)

        self._middleware.append(middleware)

    def create_bridge(self) -> WebviewBridge:
        """Create and initialize the WebviewBridge with current middleware."""
        # Use shared_threads if provided, otherwise let WebviewBridge use its default
        if self.shared_threads is not None:
            bridge = WebviewBridge(
                webview=self,
                middleware_chain=tuple(self._middleware),
                threads=self.shared_threads,
            )
        else:
            bridge = WebviewBridge(
                webview=self,
                middleware_chain=tuple(self._middleware),
                threads={},
            )
        self._bridge = bridge

        return bridge

    # Legacy methods for compatibility
    def set_size(self, value: Size) -> None:
        """Set the webview size (legacy compatibility)."""
        _webview_lib.webview_set_size(
            self.handle,
            value.width,
            value.height,
            value.hint,
        )

    def set_title(self, value: str) -> None:
        """Set the webview title (legacy compatibility)."""
        _webview_lib.webview_set_title(self.handle, _encode_c_string(value))

    def destroy(self) -> None:
        """Destroy the webview."""
        for name in list(self.callbacks.keys()):
            self.unbind(name)
        _webview_lib.webview_terminate(self.handle)
        _webview_lib.webview_destroy(self.handle)
        # Can't set _handle to None on frozen dataclass

    def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        _webview_lib.webview_navigate(self.handle, _encode_c_string(url))

    def run(self) -> None:
        """Run the webview."""
        _webview_lib.webview_run(self.handle)
        log.info("Shutting down webview...")
        self.destroy()

    def bind_jsonschema_api(self, api: MethodRegistry) -> None:
        for name in api.functions:
            wrapper = functools.partial(
                self.api_wrapper,
                name,
            )
            c_callback = _webview_lib.binding_callback_t(wrapper)

            self.add_callback(name, c_callback)

            _webview_lib.webview_bind(
                self.handle,
                _encode_c_string(name),
                c_callback,
                None,
            )

    def bind(self, name: str, callback: Callable[..., Any]) -> None:
        def wrapper(seq: bytes, req: bytes, _arg: int) -> None:
            args = json.loads(req.decode())
            try:
                result = callback(*args)
                success = True
            except Exception as e:  # noqa: BLE001
                result = str(e)
                success = False
            self.return_(seq.decode(), 0 if success else 1, json.dumps(result))

        c_callback = _webview_lib.binding_callback_t(wrapper)
        self.add_callback(name, c_callback)
        _webview_lib.webview_bind(self.handle, _encode_c_string(name), c_callback, None)

    def get_native_handle(
        self, kind: NativeHandleKind = NativeHandleKind.UI_WINDOW
    ) -> int | None:
        """Get the native handle (platform-dependent).

        Args:
            kind: Handle kind - NativeHandleKind enum value

        Returns:
            Native handle as integer, or None if failed

        """
        handle = _webview_lib.webview_get_native_handle(self.handle, kind.value)
        return handle if handle else None

    def unbind(self, name: str) -> None:
        if name in self.callbacks:
            _webview_lib.webview_unbind(self.handle, _encode_c_string(name))
            self.delete_callback(name)

    def return_(self, seq: str, status: int, result: str) -> None:
        _webview_lib.webview_return(
            self.handle,
            _encode_c_string(seq),
            status,
            _encode_c_string(result),
        )

    def eval(self, source: str) -> None:
        _webview_lib.webview_eval(self.handle, _encode_c_string(source))

    # URL filtering methods
    def add_url_pattern(self, pattern: str) -> int:
        """Add a regex pattern to the URL whitelist.

        Args:
            pattern: POSIX extended regular expression pattern.

        Returns:
            0 on success, error code otherwise.

        """
        return _webview_lib.webview_add_url_pattern(
            self.handle, _encode_c_string(pattern)
        )

    def set_url_blocked_callback(self, callback: Callable[[str], None]) -> int:
        """Set a callback to be invoked when URL navigation is blocked.

        Args:
            callback: Function taking the blocked URL as argument, or None to remove.

        Returns:
            0 on success, error code otherwise.

        """

        def wrapper(_w: int, url: bytes, _arg: int) -> None:
            callback(url.decode("utf-8"))

        c_callback = _webview_lib.url_blocked_callback_t(wrapper)
        self._url_blocked_callback = c_callback  # prevent GC
        return _webview_lib.webview_set_url_blocked_callback(
            self.handle, c_callback, None
        )


if __name__ == "__main__":
    wv = Webview(title="Hello, World!")
    wv.navigate("https://www.google.com")
    wv.run()
