from collections.abc import Callable
from dataclasses import dataclass

from clan_cli.clan_uri import ClanURI


# url is only set, if the app was started with "join <url>"
# Url is usually None, when user clicks "New" clan
@dataclass
class InitialJoinValues:
    url: ClanURI | None


@dataclass
class Callbacks:
    show_list: Callable[[], None]
    show_join: Callable[[], None]
    spawn_vm: Callable[[str, str], None]
    stop_vm: Callable[[str, str], None]
    running_vms: Callable[[], list[str]]
