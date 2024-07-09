from dataclasses import dataclass

import gi

gi.require_version("Gtk", "4.0")


@dataclass
class ClanConfig:
    initial_view: str
    content_uri: str
