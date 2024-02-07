from dataclasses import dataclass
from enum import StrEnum

import gi

gi.require_version("Gtk", "4.0")


@dataclass
class ClanConfig:
    initial_view: str


class VMStatus(StrEnum):
    RUNNING = "Running"
    STOPPED = "Stopped"
