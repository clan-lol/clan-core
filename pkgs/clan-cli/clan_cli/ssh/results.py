from dataclasses import dataclass
from typing import Generic

from clan_lib.errors import CmdOut
from clan_lib.ssh.remote import Remote

from clan_cli.ssh import T


@dataclass
class HostResult(Generic[T]):
    host: Remote
    _result: T | Exception

    @property
    def error(self) -> Exception | None:
        """
        Returns an error if the command failed
        """
        if isinstance(self._result, Exception):
            return self._result
        return None

    @property
    def result(self) -> T:
        """
        Unwrap the result
        """
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


Results = list[HostResult[CmdOut]]
