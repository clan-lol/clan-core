from enum import Enum
from typing import Any


class Tags(Enum):
    flake = "flake"
    machine = "machine"
    vm = "vm"
    modules = "modules"
    root = "root"

    def __str__(self) -> str:
        return self.value


tags_metadata: list[dict[str, Any]] = [
    {
        "name": str(Tags.flake),
        "description": "Operations on a flake.",
        "externalDocs": {
            "description": "What is a flake?",
            "url": "https://www.tweag.io/blog/2020-05-25-flakes/",
        },
    },
    {
        "name": str(Tags.machine),
        "description": "Manage physical machines. Instances of a flake",
    },
    {
        "name": str(Tags.vm),
        "description": "Manage virtual machines. Instances of a flake",
    },
    {
        "name": str(Tags.modules),
        "description": "Manage cLAN modules of a flake",
    },
]
