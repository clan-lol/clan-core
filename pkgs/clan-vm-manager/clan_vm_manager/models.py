from collections import OrderedDict
from pathlib import Path
from typing import Any

import clan_cli


class VM:
    def __init__(
        self,
        *,
        icon: Path,
        name: str,
        url: str,
        path: Path,
        running: bool = False,
        autostart: bool = False,
    ) -> None:
        self.icon = icon.resolve()
        assert self.icon.exists()
        assert self.icon.is_file()
        self.url = url
        self.autostart = autostart
        self.running = running
        self.name = name

        self.path = path.resolve()
        print(self.path)
        assert self.path.exists()
        assert self.path.is_dir()

    def list_display(self) -> OrderedDict[str, Any]:
        return OrderedDict(
            {
                "Icon": str(self.icon),
                "Name": self.name,
                "URL": self.url,
                "Running": self.running,
            }
        )


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
        ),
        VM(
            icon=assets / "firestorm.jpeg",
            name="Firestorm Clan",
            url="clan://firestorm.lol",
            path=Path(__file__).parent.parent / "test_democlan",
        ),
        VM(
            icon=assets / "placeholder.jpeg",
            name="Demo Clan",
            url="clan://demo.lol",
            path=Path(__file__).parent.parent / "test_democlan",
        ),
    ]
    # vms.extend(vms)
    # vms.extend(vms)
    # vms.extend(vms)

    for path in clan_cli.flakes.history.list_history():
        new_vm = {
            "icon": assets / "placeholder.jpeg",
            "name": "Placeholder Clan",
            "url": "clan://placeholder.lol",
            "path": path,
        }
        vms.append(VM(**new_vm))
    return vms
