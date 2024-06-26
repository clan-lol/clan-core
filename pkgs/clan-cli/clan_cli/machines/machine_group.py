from collections.abc import Callable
from typing import TypeVar

from ..ssh import Host, HostGroup, HostResult
from .machines import Machine

T = TypeVar("T")


class MachineGroup:
    def __init__(self, machines: list[Machine]) -> None:
        self.group = HostGroup(list(m.target_host for m in machines))

    def run_function(
        self, func: Callable[[Machine], T], check: bool = True
    ) -> list[HostResult[T]]:
        """
        Function to run for each host in the group in parallel

        @func the function to call
        """

        def wrapped_func(host: Host) -> T:
            return func(host.meta["machine"])

        return self.group.run_function(wrapped_func, check=check)
