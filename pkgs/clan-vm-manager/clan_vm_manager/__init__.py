import argparse
from typing import Callable, Optional

start_app: Optional[Callable] = None

from .app import start_app


def main() -> None:
    parser = argparse.ArgumentParser(description="clan-vm-manager")
    parser.set_defaults(func=start_app)
    args = parser.parse_args()
    args.func(args)
