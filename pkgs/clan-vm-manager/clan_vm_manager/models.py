from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import gi
from clan_cli import flakes, vms, history

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf

from clan_vm_manager import assets


@dataclass(frozen=True)
class VMBase:
    icon: Path | GdkPixbuf.Pixbuf
    name: str
    url: str
    status: bool
    _path: Path

    @staticmethod
    def name_to_type_map() -> OrderedDict[str, type]:
        return OrderedDict(
            {
                "Icon": GdkPixbuf.Pixbuf,
                "Name": str,
                "URL": str,
                "Online": bool,
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
                "Online": self.status,
                "_Path": str(self._path),
            }
        )

    def run(self) -> None:
        print(f"Running VM {self.name}")
        import asyncio

        # raise Exception("Cannot run VMs yet")
        vm = asyncio.run(
            vms.run.inspect_vm(flake_url=self._path, flake_attr="defaultVM")
        )
        vms.run.run_vm(vm)


#        for line in task.log_lines():
#            print(line, end="")


@dataclass(frozen=True)
class VM:
    # Inheritance is bad. Lets use composition
    # Added attributes are separated from base attributes.
    base: VMBase
    autostart: bool = False
    description: str | None = None


# start/end indexes can be used optionally for pagination
def get_initial_vms(start: int = 0, end: int | None = None) -> list[VM]:
    vm_list = []

    # TODO: list_history() should return a list of dicts, not a list of paths
    # Execute `clan flakes add <path>` to democlan for this to work
    for entry in history.list.list_history():
        flake_config = flakes.inspect.inspect_flake(entry.path, "defaultVM")
        vm_config = vms.inspect.inspect_vm(entry.path, "defaultVM")

        # if flake_config.icon is None:
        #     icon = assets.loc / "placeholder.jpeg"
        # else:
        #     icon = flake_config.icon
        icon = assets.loc / "placeholder.jpeg"
        # TODO: clan flakes inspect currently points to an icon that doesn't exist
        # the reason being that the icon is not in the nix store, as the democlan has
        # not been built yet. Not sure how to handle this.
        # I think how to do this is to add democlan as a flake.nix dependency and then
        # put it into the devshell.

        print(f"Icon: {icon}")
        new_vm = {
            "icon": icon,
            "name": vm_config.clan_name,
            "url": flake_config.flake_url,
            "_path": entry.path,
            "status": False,
        }
        vm_list.append(VM(base=VMBase(**new_vm)))

    # start/end slices can be used for pagination
    return vm_list[start:end]
