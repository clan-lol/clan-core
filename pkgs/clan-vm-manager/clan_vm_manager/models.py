from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import gi
from clan_cli import history

gi.require_version("GdkPixbuf", "2.0")

from gi.repository import GdkPixbuf

from clan_vm_manager import assets


# Define a function that writes to the memfd
def dummy_f() -> None:
    import sys
    import time

    c = 0
    while True:  # Simulate a long running process
        print(f"out: Hello from process c={c}", file=sys.stdout)
        print(f"err: Hello from process c={c}", file=sys.stderr)
        user = input("Enter to continue: \n")
        if user == "q":
            raise Exception("User quit")
        print(f"User entered {user}", file=sys.stdout)
        print(f"User entered {user}", file=sys.stderr)
        time.sleep(1)  # Wait for 1 second
        c += 1


@dataclass(frozen=True)
class VMBase:
    icon: Path | GdkPixbuf.Pixbuf
    name: str
    url: str
    status: bool

    @staticmethod
    def name_to_type_map() -> OrderedDict[str, type]:
        return OrderedDict(
            {
                "Icon": GdkPixbuf.Pixbuf,
                "Name": str,
                "URL": str,
                "Online": bool,
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
            }
        )

    def run(self) -> None:
        print(f"Running VM {self.name}")
        # vm = vms.run.inspect_vm(flake_url=self.url, flake_attr="defaultVM")
        import os

        from .executor import spawn

        # proc = spawn(vms.run.run_vm, vm=vm)
        proc = spawn(wait_stdin_connect=True, func=dummy_f)

        pid = os.getpid()
        gpid = os.getpgid(pid)
        print(f"Main  pid={pid}  gpid={gpid}")
        assert proc.proc.pid is not None
        gpid = os.getpgid(proc.proc.pid)
        print(f"Child pid={proc.proc.pid}  gpid={gpid}")
        # os.killpg(gpid, signal.SIGKILL)


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

    # Execute `clan flakes add <path>` to democlan for this to work
    for entry in history.list.list_history():
        icon = assets.loc / "placeholder.jpeg"
        if entry.flake.icon is not None:
            icon = entry.flake.icon

        base = VMBase(
            icon=icon,
            name=entry.flake.clan_name,
            url=entry.flake.flake_url,
            status=False,
        )
        vm_list.append(VM(base=base))

    # start/end slices can be used for pagination
    return vm_list[start:end]
