import argparse

# statement that doesn't need testing
__version__ = "1.0.0"  # pragma: no cover


# this will be an entrypoint under /bin/my_cli (see pyproject.toml config)
def my_cli() -> None:
    parser = argparse.ArgumentParser(description="my-tool")
    parser.add_argument(
        "-v", "--version", help="Show the version of this program", action="store_true"
    )
    args = parser.parse_args()
    if args.version:
        print(f"Version: {__version__}")
    else:
        parser.print_help()
