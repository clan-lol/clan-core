from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import clan_cli
import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf

from clan_vm_manager import assets


class Status(Enum):
    OFF = "Off"
    RUNNING = "Running"
    # SUSPENDED = "Suspended"
    # UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class VMBase:
    icon: Path | GdkPixbuf.Pixbuf
    name: str
    url: str
    status: Status
    _path: Path

    @staticmethod
    def name_to_type_map() -> OrderedDict[str, type]:
        return OrderedDict(
            {
                "Icon": GdkPixbuf.Pixbuf,
                "Name": str,
                "URL": str,
                "Status": str,
                "_Path": str,
            }
        )

    @staticmethod
    def to_idx(name: str) -> int:
        return list(VMBase.name_to_type_map().keys()).index(name)

    def list_data(self) -> OrderedDict[str, Any]:
        return OrderedDict(
            {
                "Icon": str(self.icon),
                "Name": self.name,
                "URL": self.url,
                "Status": str(self.status),
                "_Path": str(self._path),
            }
        )

    def run(self) -> None:
        print(f"Running VM {self.name}")
        import asyncio

        from clan_cli import vms

        # raise Exception("Cannot run VMs yet")
        vm = asyncio.run(
            vms.run.inspect_vm(flake_url=self._path, flake_attr="defaultVM")
        )
        task = vms.run.run_vm(vm)
        for line in task.log_lines():
            print(line, end="")


@dataclass(frozen=True)
class VM:
    # Inheritance is bad. Lets use composition
    # Added attributes are separated from base attributes.
    base: VMBase
    autostart: bool = False


# start/end indexes can be used optionally for pagination
def get_initial_vms(start: int = 0, end: int | None = None) -> list[VM]:
    vms = [
        VM(
            base=VMBase(
                icon=assets.loc / "cybernet.jpeg",
                name="Cybernet Clan",
                url="clan://cybernet.lol",
                _path=Path(__file__).parent.parent / "test_democlan",
                status=Status.RUNNING,
            ),
        ),
        VM(
            base=VMBase(
                icon=assets.loc / "zenith.jpeg",
                name="Zenith Clan",
                url="clan://zenith.lol",
                _path=Path(__file__).parent.parent / "test_democlan",
                status=Status.OFF,
            )
        ),
        VM(
            base=VMBase(
                icon=assets.loc / "firestorm.jpeg",
                name="Firestorm Clan",
                url="clan://firestorm.lol",
                _path=Path(__file__).parent.parent / "test_democlan",
                status=Status.OFF,
            ),
        ),
        VM(
            base=VMBase(
                icon=assets.loc / "placeholder.jpeg",
                name="Placeholder Clan",
                url="clan://demo.lol",
                _path=Path(__file__).parent.parent / "test_democlan",
                status=Status.OFF,
            ),
        ),
    ]

    # TODO: list_history() should return a list of dicts, not a list of paths
    # Execute `clan flakes add <path>` to democlan for this to work
    for entry in clan_cli.flakes.history.list_history():
        new_vm = {
            "icon": assets.loc / "placeholder.jpeg",
            "name": "Demo Clan",
            "url": "clan://demo.lol",
            "_path": entry.path,
            "status": Status.OFF,
        }
        vms.append(VM(base=VMBase(**new_vm)))

    # start/end slices can be used for pagination
    return vms[start:end]
