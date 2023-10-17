import argparse
import inspect
import logging
import shlex

from clan_cli import create_parser

log = logging.getLogger(__name__)


def get_caller() -> str:
    frame = inspect.currentframe()
    if frame is None:
        return "unknown"
    caller_frame = frame.f_back
    if caller_frame is None:
        return "unknown"
    caller_frame = caller_frame.f_back
    if caller_frame is None:
        return "unknown"
    frame_info = inspect.getframeinfo(caller_frame)
    ret = f"{frame_info.filename}:{frame_info.lineno}::{frame_info.function}"
    return ret


class Cli:
    def __init__(self) -> None:
        self.parser = create_parser(prog="clan")

    def run(self, args: list[str]) -> argparse.Namespace:
        cmd = shlex.join(["clan"] + args)
        log.debug(f"$ {cmd}")
        log.debug(f"Caller {get_caller()}")
        parsed = self.parser.parse_args(args)
        if hasattr(parsed, "func"):
            parsed.func(parsed)
        return parsed
