import argparse
from typing import Callable, Optional

start_app: Optional[Callable] = None

from .app import start_app


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=start_app)
