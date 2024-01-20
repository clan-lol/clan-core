from dataclasses import dataclass
from enum import StrEnum

import gi
from clan_cli.clan_uri import ClanURI

gi.require_version("Gtk", "4.0")


@dataclass
class InitialJoinValues:
    url: ClanURI | None


@dataclass
class ClanConfig:
    initial_view: str
    url: ClanURI | None


class VMStatus(StrEnum):
    RUNNING = "Running"
    STOPPED = "Stopped"
