# ruff: noqa: TRY301
import functools
import io
import json
import logging
import threading
from collections.abc import Callable
from enum import IntEnum
from typing import Any

from clan_lib.api import (
    ApiError,
    ErrorDataClass,
    MethodRegistry,
    dataclass_to_dict,
    from_dict,
)
from clan_lib.api.tasks import WebThread
from clan_lib.async_run import AsyncContext, get_async_ctx, set_async_ctx
from clan_lib.custom_logger import setup_logging
from clan_lib.log_manager import LogManager

from ._webview_ffi import _encode_c_string, _webview_lib

log = logging.getLogger(__name__)


class SizeHint(IntEnum):
    NONE = 0
    MIN = 1
    MAX = 2
    FIXED = 3


class FuncStatus(IntEnum):
    SUCCESS = 0
    FAILURE = 1


class Size:
    def __init__(self, width: int, height: int, hint: SizeHint) -> None:
        self.width = width
        self.height = height
        self.hint = hint


class Webview:
    def __init__(
        self, debug: bool = False, size: Size | None = None, window: int | None = None
    ) -> None:
        self._handle = _webview_lib.webview_create(int(debug), window)
        self._callbacks: dict[str, Callable[..., Any]] = {}
        self.threads: dict[str, WebThread] = {}

        if size:
            self.size = size

    def api_wrapper(
        self,
        log_manager: LogManager,
        api: MethodRegistry,
        method_name: str,
        wrap_method: Callable[..., Any],
        op_key_bytes: bytes,
        request_data: bytes,
        arg: int,
    ) -> None:
        op_key = op_key_bytes.decode()
        args = json.loads(request_data.decode())
        log.debug(f"Calling {method_name}({json.dumps(args, indent=4)})")
        header: dict[str, Any]

        try:
            # Initialize dataclasses from the payload
            reconciled_arguments = {}
            if len(args) == 1:
                request = args[0]
                header = request.get("header", {})
                msg = f"Expected header to be a dict, got {type(header)}"
                if not isinstance(header, dict):
                    raise TypeError(msg)
                body = request.get("body", {})
                msg = f"Expected body to be a dict, got {type(body)}"
                if not isinstance(body, dict):
                    raise TypeError(msg)

                for k, v in body.items():
                    # Some functions expect to be called with dataclass instances
                    # But the js api returns dictionaries.
                    # Introspect the function and create the expected dataclass from dict dynamically
                    # Depending on the introspected argument_type
                    arg_class = api.get_method_argtype(method_name, k)

                    # TODO: rename from_dict into something like construct_checked_value
                    # from_dict really takes Anything and returns an instance of the type/class
                    reconciled_arguments[k] = from_dict(arg_class, v)
            elif len(args) > 1:
                msg = (
                    "Expected a single argument, got multiple arguments to api_wrapper"
                )
                raise ValueError(msg)

            reconciled_arguments["op_key"] = op_key
        except Exception as e:
            log.exception(f"Error while parsing arguments for {method_name}")
            result = ErrorDataClass(
                op_key=op_key,
                status="error",
                errors=[
                    ApiError(
                        message="An internal error occured",
                        description=str(e),
                        location=["bind_jsonschema_api", method_name],
                    )
                ],
            )
            serialized = json.dumps(
                dataclass_to_dict(result), indent=4, ensure_ascii=False
            )
            self.return_(op_key, FuncStatus.SUCCESS, serialized)
            return

        def thread_task(stop_event: threading.Event) -> None:
            ctx: AsyncContext = get_async_ctx()
            ctx.should_cancel = lambda: stop_event.is_set()

            try:
                # If the API call has set log_group in metadata,
                # create the log file under that group.
                log_group: list[str] = header.get("logging", {}).get("group_path", None)
                if log_group is not None:
                    if not isinstance(log_group, list):
                        msg = f"Expected log_group to be a list, got {type(log_group)}"
                        raise TypeError(msg)
                    log.warning(
                        f"Using log group {log_group} for {method_name} with op_key {op_key}"
                    )

                log_file = log_manager.create_log_file(
                    wrap_method, op_key=op_key, group_path=log_group
                ).get_file_path()
            except Exception as e:
                log.exception(f"Error while handling request header of {method_name}")
                result = ErrorDataClass(
                    op_key=op_key,
                    status="error",
                    errors=[
                        ApiError(
                            message="An internal error occured",
                            description=str(e),
                            location=["header_middleware", method_name],
                        )
                    ],
                )
                serialized = json.dumps(
                    dataclass_to_dict(result), indent=4, ensure_ascii=False
                )
                self.return_(op_key, FuncStatus.SUCCESS, serialized)

            with log_file.open("ab") as log_f:
                # Redirect all cmd.run logs to this file.
                ctx.stderr = log_f
                ctx.stdout = log_f
                set_async_ctx(ctx)

                # Add a new handler to the root logger that writes to log_f
                handler_stream = io.TextIOWrapper(
                    log_f, encoding="utf-8", write_through=True, line_buffering=True
                )
                handler = setup_logging(
                    log.getEffectiveLevel(), log_file=handler_stream
                )

                try:
                    # Original logic: call the wrapped API method.
                    result = wrap_method(**reconciled_arguments)
                    wrapped_result = {"body": dataclass_to_dict(result), "header": {}}

                    # Serialize the result to JSON.
                    serialized = json.dumps(
                        dataclass_to_dict(wrapped_result), indent=4, ensure_ascii=False
                    )

                    # This log message will now also be written to log_f
                    # through the thread_log_handler.
                    log.debug(f"Result for {method_name}: {serialized}")

                    # Return the successful result.
                    self.return_(op_key, FuncStatus.SUCCESS, serialized)
                except Exception as e:
                    log.exception(f"Error while handling result of {method_name}")
                    result = ErrorDataClass(
                        op_key=op_key,
                        status="error",
                        errors=[
                            ApiError(
                                message="An internal error occured",
                                description=str(e),
                                location=["bind_jsonschema_api", method_name],
                            )
                        ],
                    )
                    serialized = json.dumps(
                        dataclass_to_dict(result), indent=4, ensure_ascii=False
                    )
                    self.return_(op_key, FuncStatus.SUCCESS, serialized)
                finally:
                    # Crucial cleanup: remove the handler from the root logger.
                    # This stops redirecting logs for this thread to log_f and prevents
                    # the handler from being used after log_f is closed.
                    handler.root_logger.removeHandler(handler.new_handler)
                    # Close the handler. For a StreamHandler using a stream it doesn't
                    # own (log_f is managed by the 'with' statement), this typically
                    # flushes the stream.
                    handler.new_handler.close()
                    del self.threads[op_key]

        stop_event = threading.Event()
        thread = threading.Thread(
            target=thread_task, args=(stop_event,), name="WebviewThread"
        )
        thread.start()
        self.threads[op_key] = WebThread(thread=thread, stop_event=stop_event)

    def __enter__(self) -> "Webview":
        return self

    @property
    def size(self) -> Size:
        return self._size

    @size.setter
    def size(self, value: Size) -> None:
        _webview_lib.webview_set_size(
            self._handle, value.width, value.height, value.hint
        )
        self._size = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        _webview_lib.webview_set_title(self._handle, _encode_c_string(value))
        self._title = value

    def destroy(self) -> None:
        for name in list(self._callbacks.keys()):
            self.unbind(name)
        _webview_lib.webview_terminate(self._handle)
        _webview_lib.webview_destroy(self._handle)
        self._handle = None

    def navigate(self, url: str) -> None:
        _webview_lib.webview_navigate(self._handle, _encode_c_string(url))

    def run(self) -> None:
        _webview_lib.webview_run(self._handle)
        log.info("Shutting down webview...")
        self.destroy()

    def bind_jsonschema_api(self, api: MethodRegistry, log_manager: LogManager) -> None:
        for name, method in api.functions.items():
            wrapper = functools.partial(
                self.api_wrapper,
                log_manager,
                api,
                name,
                method,
            )
            c_callback = _webview_lib.binding_callback_t(wrapper)

            if name in self._callbacks:
                msg = f"Callback {name} already exists. Skipping binding."
                raise RuntimeError(msg)

            self._callbacks[name] = c_callback
            _webview_lib.webview_bind(
                self._handle, _encode_c_string(name), c_callback, None
            )

    def bind(self, name: str, callback: Callable[..., Any]) -> None:
        def wrapper(seq: bytes, req: bytes, arg: int) -> None:
            args = json.loads(req.decode())
            try:
                result = callback(*args)
                success = True
            except Exception as e:
                result = str(e)
                success = False
            self.return_(seq.decode(), 0 if success else 1, json.dumps(result))

        c_callback = _webview_lib.binding_callback_t(wrapper)
        self._callbacks[name] = c_callback
        _webview_lib.webview_bind(
            self._handle, _encode_c_string(name), c_callback, None
        )

    def unbind(self, name: str) -> None:
        if name in self._callbacks:
            _webview_lib.webview_unbind(self._handle, _encode_c_string(name))
            del self._callbacks[name]

    def return_(self, seq: str, status: int, result: str) -> None:
        _webview_lib.webview_return(
            self._handle, _encode_c_string(seq), status, _encode_c_string(result)
        )

    def eval(self, source: str) -> None:
        _webview_lib.webview_eval(self._handle, _encode_c_string(source))

    def init(self, source: str) -> None:
        _webview_lib.webview_init(self._handle, _encode_c_string(source))


if __name__ == "__main__":
    wv = Webview()
    wv.title = "Hello, World!"
    wv.navigate("https://www.google.com")
    wv.run()
