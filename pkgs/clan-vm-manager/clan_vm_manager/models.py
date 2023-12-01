from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import clan_cli
from gi.repository import GdkPixbuf


@dataclass(frozen=True)
class VMBase:
    icon: Path | GdkPixbuf.Pixbuf
    name: str
    url: str
    running: bool

    @staticmethod
    def name_to_type_map() -> OrderedDict[str, type]:
        return OrderedDict(
            {
                "Icon": GdkPixbuf.Pixbuf,
                "Name": str,
                "URL": str,
                "Running": bool,
            }
        )

    def list_data(self) -> OrderedDict[str, Any]:
        return OrderedDict(
            {
                "Icon": str(self.icon),
                "Name": self.name,
                "URL": self.url,
                "Running": self.running,
            }
        )


@dataclass(frozen=True)
class VM(VMBase):
    path: Path
    autostart: bool = False


def list_vms() -> list[VM]:
    assets = Path(__file__).parent / "assets"

    vms = [
        VM(
            icon=assets / "cybernet.jpeg",
            name="Cybernet Clan",
            url="clan://cybernet.lol",
            path=Path(__file__).parent.parent / "test_democlan",
            running=True,
        ),
        VM(
            icon=assets / "zenith.jpeg",
            name="Zenith Clan",
            url="clan://zenith.lol",
            path=Path(__file__).parent.parent / "test_democlan",
            running=False,
        ),
        VM(
            icon=assets / "firestorm.jpeg",
            name="Firestorm Clan",
            url="clan://firestorm.lol",
            path=Path(__file__).parent.parent / "test_democlan",
            running=False,
        ),
        VM(
            icon=assets / "placeholder.jpeg",
            name="Demo Clan",
            url="clan://demo.lol",
            path=Path(__file__).parent.parent / "test_democlan",
            running=False,
        ),
    ]

    for path in clan_cli.flakes.history.list_history():
        new_vm = {
            "icon": assets / "placeholder.jpeg",
            "name": "Placeholder Clan",
            "url": "clan://placeholder.lol",
            "path": path,
        }
        vms.append(VM(**new_vm))
    return vms
