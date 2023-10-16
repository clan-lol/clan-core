import argparse

from clan_cli import create_parser
import logging
import sys
import shlex
log = logging.getLogger(__name__)

import inspect

def get_caller() -> str:
    frame = inspect.currentframe()
    caller_frame = frame.f_back.f_back
    frame_info = inspect.getframeinfo(caller_frame)
    ret = f"{frame_info.filename}:{frame_info.lineno}::{frame_info.function}"
    return ret


class Cli:
    def __init__(self) -> None:
        self.parser = create_parser(prog="clan")

    def run(self, args: list[str]) -> argparse.Namespace:
        cmd = shlex.join(["clan"] + args)
        log.debug(f"Command: {cmd}")
        log.debug(f"Caller {get_caller()}")
        parsed = self.parser.parse_args(args)
        if hasattr(parsed, "func"):
            parsed.func(parsed)
        return parsed
