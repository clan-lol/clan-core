import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import clan_cli
from clan_cli import vms
from gi.repository import GdkPixbuf


@dataclass(frozen=True)
class VMBase:
    icon: Path | GdkPixbuf.Pixbuf
    name: str
    url: str
    running: bool
    _path: Path

    @staticmethod
    def name_to_type_map() -> OrderedDict[str, type]:
        return OrderedDict(
            {
                "Icon": GdkPixbuf.Pixbuf,
                "Name": str,
                "URL": str,
                "Running": bool,
                "_Path": str,
            }
        )

    def list_data(self) -> OrderedDict[str, Any]:
        return OrderedDict(
            {
                "Icon": str(self.icon),
                "Name": self.name,
                "URL": self.url,
                "Running": self.running,
                "_Path": str(self._path),
            }
        )

    def run(self) -> None:
        print(f"Running VM {self.name}")
        vm = asyncio.run(vms.run.inspect_vm(flake_url=self._path, flake_attr="defaultVM"))
        task = vms.run.run_vm(vm)
        for line in task.log_lines():
            print(line, end="")




@dataclass(frozen=True)
class VM(VMBase):
    autostart: bool = False


def list_vms() -> list[VM]:
    assets = Path(__file__).parent / "assets"

    vms = [
        VM(
            icon=assets / "cybernet.jpeg",
            name="Cybernet Clan",
            url="clan://cybernet.lol",
            _path=Path(__file__).parent.parent / "test_democlan",
            running=True,
        ),
        VM(
            icon=assets / "zenith.jpeg",
            name="Zenith Clan",
            url="clan://zenith.lol",
            _path=Path(__file__).parent.parent / "test_democlan",
            running=False,
        ),
        VM(
            icon=assets / "firestorm.jpeg",
            name="Firestorm Clan",
            url="clan://firestorm.lol",
            _path=Path(__file__).parent.parent / "test_democlan",
            running=False,
        ),
        VM(
            icon=assets / "placeholder.jpeg",
            name="Placeholder Clan",
            url="clan://demo.lol",
            _path=Path(__file__).parent.parent / "test_democlan",
            running=False,
        ),
    ]


    # TODO: list_history() should return a list of dicts, not a list of paths
    # Execute `clan flakes add <path>` to democlan for this to work
    for path in clan_cli.flakes.history.list_history():
        new_vm = {
            "icon": assets / "placeholder.jpeg",
            "name": "Demo Clan",
            "url": "clan://demo.lol",
            "_path": path,
            "running": False,
        }
        vms.append(VM(**new_vm))
    return vms
