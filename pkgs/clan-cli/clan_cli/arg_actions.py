import argparse
import logging
from collections.abc import Sequence
from typing import Any

log = logging.getLogger(__name__)


class AppendOptionAction(argparse.Action):
    def __init__(self, option_strings: str, dest: str, **kwargs: Any) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        lst = getattr(namespace, self.dest)
        lst.append("--option")
        assert isinstance(values, list), "values must be a list"
        lst.append(values[0])
        lst.append(values[1])
