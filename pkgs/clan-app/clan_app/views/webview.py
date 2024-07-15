import dataclasses
import json
import logging
from collections.abc import Callable
from typing import Any

import gi
from clan_cli.api import API

import clan_app
from clan_app.api import GResult, ImplApi, ImplFunc
from clan_app.components.serializer import dataclass_to_dict, from_dict

gi.require_version("WebKit", "6.0")
from gi.repository import GLib, GObject, WebKit

log = logging.getLogger(__name__)


class WebExecutor(GObject.Object):
    def __init__(self, content_uri: str, abstr_methods: dict[str, Callable]) -> None:
        super().__init__()

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        # settings.
        settings.set_property("enable-developer-extras", True)
        self.webview.set_settings(settings)
        # Fixme. This filtering is incomplete, it only triggers if a user clicks a link
        self.webview.connect("decide-policy", self.on_decide_policy)

        self.manager = self.webview.get_user_content_manager()
        # Can be called with: window.webkit.messageHandlers.gtk.postMessage("...")
        # Important: it seems postMessage must be given some payload, otherwise it won't trigger the event
        self.manager.register_script_message_handler("gtk")
        self.manager.connect("script-message-received", self.on_message_received)

        self.webview.load_uri(content_uri)
        self.content_uri = content_uri

        self.api = ImplApi()
        self.api.register_all(clan_app.api)
        #self.api.validate(abstr_methods)


    def on_decide_policy(
        self,
        webview: WebKit.WebView,
        decision: WebKit.PolicyDecision,
        decision_type: WebKit.PolicyDecisionType,
    ) -> bool:
        if decision_type != WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            return False  # Continue with the default handler

        navigation_action = decision.get_navigation_action()
        request = navigation_action.get_request()
        uri = request.get_uri()
        if self.content_uri.startswith("http://") and uri.startswith(self.content_uri):
            log.debug(f"Allow navigation request: {uri}")
            return False
        elif self.content_uri.startswith("file://") and uri.startswith(
            self.content_uri
        ):
            log.debug(f"Allow navigation request: {uri}")
            return False
        log.warning(
            f"Do not allow navigation request: {uri}. Current content uri: {self.content_uri}"
        )
        decision.ignore()
        return True  # Stop other handlers from being invoked

    def on_message_received(
        self, user_content_manager: WebKit.UserContentManager, message: Any
    ) -> None:
        json_msg = message.to_json(4)
        log.debug(f"Webview Request: {json_msg}")
        payload = json.loads(json_msg)
        method_name = payload["method"]

        # Get the function gobject from the api
        function_obj = self.api.get_obj(method_name)
        if function_obj is None:
            log.error(f"Method '{method_name}' not found in api")
            return

        # Create an instance of the function gobject
        fn_instance = function_obj()
        fn_instance.await_result(self.on_result)

        # Extract the data from the payload
        data = payload.get("data")
        if data is None:
            log.error(f"Method '{method_name}' has no data field. Skipping execution.")
            return

        # Initialize dataclasses from the payload
        reconciled_arguments = {}
        op_key = data.pop("op_key", None)
        for k, v in data.items():
            # Some functions expect to be called with dataclass instances
            # But the js api returns dictionaries.
            # Introspect the function and create the expected dataclass from dict dynamically
            # Depending on the introspected argument_type
            arg_class = API.get_method_argtype(method_name, k)
            if dataclasses.is_dataclass(arg_class):
                reconciled_arguments[k] = from_dict(arg_class, v)
            else:
                reconciled_arguments[k] = v

        GLib.idle_add(
            fn_instance._async_run,
            reconciled_arguments,
            op_key,
        )


    def on_result(self, source: ImplFunc, data: GResult) -> None:
        result = dict()
        result["result"] = dataclass_to_dict(data.result)
        result["op_key"] = data.op_key

        serialized = json.dumps(result, indent=4)
        log.debug(f"Result: {serialized}")
        # Use idle_add to queue the response call to js on the main GTK thread
        self.return_data_to_js(data.method_name, serialized)

    def return_data_to_js(self, method_name: str, serialized: str) -> bool:
        self.webview.evaluate_javascript(
            f"""
            window.clan.{method_name}(`{serialized}`);
            """,
            -1,
            None,
            None,
            None,
        )
        return GLib.SOURCE_REMOVE

    def get_webview(self) -> WebKit.WebView:
        return self.webview
