# !/usr/bin/env python3
import argparse
import subprocess
import urllib
from typing import Optional


def join(args: argparse.Namespace) -> None:
    # start webui in background
    uri = args.flake_uri.removeprefix("clan://")
    subprocess.run(
        ["clan", "webui", f"/join?flake={urllib.parse.quote_plus(uri)}"],
        # stdout=sys.stdout,
        # stderr=sys.stderr,
    )
    print(f"joined clan {args.flake_uri}")


# takes a (sub)parser and configures it
def register_parser(
    parser: Optional[argparse.ArgumentParser],
) -> None:
    if parser is None:
        parser = argparse.ArgumentParser(
            description="join a remote clan",
        )

    # inject callback function to process the input later
    parser.set_defaults(func=join)

    parser.add_argument(
        "flake_uri",
        help="flake uri to join",
        type=str,
    )
