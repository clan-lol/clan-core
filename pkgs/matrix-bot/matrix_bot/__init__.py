import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from matrix_bot.custom_logger import setup_logging
from matrix_bot.gitea import GiteaData
from matrix_bot.main import bot_main
from matrix_bot.matrix import MatrixData

log = logging.getLogger(__name__)

curr_dir = Path(__file__).parent


def create_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="A gitea bot for matrix",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--server",
        help="The matrix server to connect to",
        default="https://matrix.clan.lol",
    )

    parser.add_argument(
        "--user",
        help="The matrix user to connect as",
        default="@clan-bot:clan.lol",
    )

    parser.add_argument(
        "--avatar",
        help="The path to the image to use as the avatar",
        default=curr_dir / "avatar.png",
    )

    parser.add_argument(
        "--repo-owner",
        help="The owner of gitea the repository",
        default="clan",
    )
    parser.add_argument(
        "--repo-name",
        help="The name of the repository",
        default="clan-core",
    )

    parser.add_argument(
        "--matrix-room",
        help="The matrix room to join",
        default="#bot-test:gchq.icu",
    )

    parser.add_argument(
        "--gitea-url",
        help="The gitea url to connect to",
        default="https://git.clan.lol",
    )

    parser.add_argument(
        "--trigger-labels",
        help="The labels that trigger the bot",
        default=["needs-review"],
        nargs="+",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.debug:
        setup_logging(logging.DEBUG, root_log_name=__name__.split(".")[0])
        log.debug("Debug log activated")
    else:
        setup_logging(logging.INFO, root_log_name=__name__.split(".")[0])

    password = os.getenv("MATRIX_PASSWORD")
    if not password:
        log.error("No password provided set the MATRIX_PASSWORD environment variable")

    matrix = MatrixData(
        server=args.server,
        user=args.user,
        avatar=args.avatar,
        room=args.matrix_room,
        password=password,
    )

    gitea = GiteaData(
        url=args.gitea_url,
        owner=args.repo_owner,
        repo=args.repo_name,
        trigger_labels=args.trigger_labels,
        access_token=os.getenv("GITEA_ACCESS_TOKEN"),
    )

    try:
        asyncio.run(bot_main(matrix, gitea))
    except KeyboardInterrupt:
        print("User Interrupt", file=sys.stderr)


if __name__ == "__main__":
    main()
