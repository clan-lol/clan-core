import ctypes
import ctypes.util
import os
import platform
from ctypes import CFUNCTYPE, c_char_p, c_int, c_void_p
from pathlib import Path

# Native handle kinds
WEBVIEW_NATIVE_HANDLE_KIND_UI_WINDOW = 0
WEBVIEW_NATIVE_HANDLE_KIND_UI_WIDGET = 1
WEBVIEW_NATIVE_HANDLE_KIND_BROWSER_CONTROLLER = 2


def _encode_c_string(s: str) -> bytes:
    return s.encode("utf-8")


def _get_webview_version() -> str:
    """Get webview version from environment variable or use default"""
    return os.getenv("WEBVIEW_VERSION", "0.8.1")


def _get_lib_names() -> list[str]:
    """Get platform-specific library names."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        if machine in {"amd64", "x86_64"}:
            return ["webview.dll", "WebView2Loader.dll"]
        if machine == "arm64":
            msg = "arm64 is not supported on Windows"
            raise RuntimeError(msg)
        msg = f"Unsupported architecture: {machine}"
        raise RuntimeError(msg)
    if system == "darwin":
        return ["libwebview.dylib"]
    # linux
    return ["libwebview.so"]


def _be_sure_libraries() -> list[Path] | None:
    """Ensure libraries exist and return paths."""
    lib_dir = os.environ.get("WEBVIEW_LIB_DIR")
    if not lib_dir:
        msg = "WEBVIEW_LIB_DIR environment variable is not set"
        raise RuntimeError(msg)
    lib_dir_p = Path(lib_dir)
    lib_names = _get_lib_names()
    lib_paths = [lib_dir_p / lib_name for lib_name in lib_names]

    # Check if any library is missing
    missing_libs = [path for path in lib_paths if not path.exists()]
    if not missing_libs:
        return lib_paths
    return None


class _WebviewLibrary:
    def __init__(self) -> None:
        lib_names = _get_lib_names()

        library_path = ctypes.util.find_library(lib_names[0])
        if not library_path:
            library_paths = _be_sure_libraries()
        if not library_paths:
            msg = f"Failed to find required library: {lib_names}"
            raise RuntimeError(msg)
        try:
            self.lib = ctypes.cdll.LoadLibrary(str(library_paths[0]))
        except Exception as e:
            print(f"Failed to load webview library: {e}")
            raise

        # Define FFI functions
        self.webview_create = self.lib.webview_create
        self.webview_create.argtypes = [c_int, c_void_p]
        self.webview_create.restype = c_void_p

        self.webview_create_with_app_id = self.lib.webview_create_with_app_id
        self.webview_create_with_app_id.argtypes = [c_int, c_void_p, c_char_p]
        self.webview_create_with_app_id.restype = c_void_p

        self.webview_destroy = self.lib.webview_destroy
        self.webview_destroy.argtypes = [c_void_p]

        self.webview_run = self.lib.webview_run
        self.webview_run.argtypes = [c_void_p]

        self.webview_terminate = self.lib.webview_terminate
        self.webview_terminate.argtypes = [c_void_p]

        self.webview_set_title = self.lib.webview_set_title
        self.webview_set_title.argtypes = [c_void_p, c_char_p]

        self.webview_set_size = self.lib.webview_set_size
        self.webview_set_size.argtypes = [c_void_p, c_int, c_int, c_int]

        self.webview_navigate = self.lib.webview_navigate
        self.webview_navigate.argtypes = [c_void_p, c_char_p]

        self.webview_init = self.lib.webview_init
        self.webview_init.argtypes = [c_void_p, c_char_p]

        self.webview_eval = self.lib.webview_eval
        self.webview_eval.argtypes = [c_void_p, c_char_p]

        self.webview_bind = self.lib.webview_bind
        self.webview_bind.argtypes = [c_void_p, c_char_p, c_void_p, c_void_p]

        self.webview_unbind = self.lib.webview_unbind
        self.webview_unbind.argtypes = [c_void_p, c_char_p]

        self.webview_return = self.lib.webview_return
        self.webview_return.argtypes = [c_void_p, c_char_p, c_int, c_char_p]

        self.webview_get_native_handle = self.lib.webview_get_native_handle
        self.webview_get_native_handle.argtypes = [c_void_p, c_int]
        self.webview_get_native_handle.restype = c_void_p

        self.binding_callback_t = CFUNCTYPE(None, c_char_p, c_char_p, c_void_p)

        self.CFUNCTYPE = CFUNCTYPE


_webview_lib = _WebviewLibrary()
