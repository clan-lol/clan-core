from collections.abc import Callable
from dataclasses import dataclass

from clan_cli.clan_uri import ClanURI


@dataclass
class InitialJoinValues:
    url: ClanURI


@dataclass
class Callbacks:
    show_list: Callable[[], None]
    show_join: Callable[[], None]
