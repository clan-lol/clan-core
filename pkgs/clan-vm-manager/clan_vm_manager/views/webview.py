import sys
from pathlib import Path
from typing import Any, List
from clan_cli import machines
import time
import gi
import json

gi.require_version("WebKit", "6.0")

from gi.repository import WebKit

site_index: Path = (Path(sys.argv[0]).absolute() / Path("../..") / Path("web/app/dist/index.html") ).resolve()


class WebView():
    def __init__(self) -> None:

        self.webview = WebKit.WebView()

        self.manager = self.webview.get_user_content_manager()
        # Can be called with: window.webkit.messageHandlers.gtk.postMessage("...")
        # Important: it seems postMessage must be given some payload, otherwise it won't trigger the event
        self.manager.register_script_message_handler("gtk")
        self.manager.connect("script-message-received", self.on_message_received)

        self.webview.load_uri(f"file://{site_index}")

    def on_message_received(
        self, user_content_manager: WebKit.UserContentManager, message: Any
    ) -> None:
        # payload = json.loads(message.to_json(0))
        # TODO: 
        # Dynamically call functions in the js context
        # I.e. the result function should have the same name as the target method in the gtk context
        # Example: 
        # request -> { method: "list_machines", data: None }
        # internally call list_machines and serialize the result
        # result -> window.clan.list_machines(`{serialized}`)

        list_of_machines = machines.list.list_machines(".")
        serialized = json.dumps(list_of_machines)
        # Important: use ` backticks to avoid escaping issues with conflicting quotes in js and json
        self.webview.evaluate_javascript(f"""
            setTimeout(() => {{ 
                window.clan.setMachines(`{serialized}`);
            }},2000);
        """, -1, None, None, None)

    def get_webview(self) -> WebKit.WebView:
        return self.webview
