# This file contains type hints that can be prepended to Nix test scripts so they can be type
# checked.

from collections.abc import Callable

from test_driver import Machine

start_all: Callable[[], None]
machines: list[Machine]
