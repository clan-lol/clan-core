import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clan_lib.api import dataclass_to_dict
from clan_lib.api.tasks import WebThread

from clan_app.api.api_bridge import ApiBridge, BackendRequest, BackendResponse

from .webview import FuncStatus

if TYPE_CHECKING:
    from .webview import Webview

log = logging.getLogger(__name__)


@dataclass
class WebviewBridge(ApiBridge):
    """Webview-specific implementation of the API bridge."""

    webview: "Webview"
    threads: dict[str, WebThread]  # Inherited from ApiBridge

    def send_api_response(self, response: BackendResponse) -> None:
        """Send response back to the webview client."""
        serialized = json.dumps(
            dataclass_to_dict(response), indent=4, ensure_ascii=False
        )

        log.debug(f"Sending response: {serialized}")
        self.webview.return_(response._op_key, FuncStatus.SUCCESS, serialized)  # noqa: SLF001

    def handle_webview_call(
        self,
        method_name: str,
        op_key_bytes: bytes,
        request_data: bytes,
        arg: int,
    ) -> None:
        """Handle a call from webview's JavaScript bridge."""

        try:
            op_key = op_key_bytes.decode()
            raw_args = json.loads(request_data.decode())

            # Parse the webview-specific request format
            header = {}
            args = {}

            if len(raw_args) == 1:
                request = raw_args[0]
                header = request.get("header", {})
                if not isinstance(header, dict):
                    msg = f"Expected header to be a dict, got {type(header)}"
                    raise TypeError(msg)  # noqa: TRY301

                body = request.get("body", {})
                if not isinstance(body, dict):
                    msg = f"Expected body to be a dict, got {type(body)}"
                    raise TypeError(msg)  # noqa: TRY301

                args = body
            elif len(raw_args) > 1:
                msg = "Expected a single argument, got multiple arguments"
                raise ValueError(msg)  # noqa: TRY301

            # Create API request
            api_request = BackendRequest(
                method_name=method_name, args=args, header=header, op_key=op_key
            )

        except Exception as e:
            msg = (
                f"Error while handling webview call {method_name} with op_key {op_key}"
            )
            log.exception(msg)
            self.send_api_error_response(
                op_key, str(e), ["webview_bridge", method_name]
            )
            return

        # Process in a separate thread using the inherited method
        self.process_request_in_thread(
            api_request,
            thread_name="WebviewThread",
            wait_for_completion=False,
        )
