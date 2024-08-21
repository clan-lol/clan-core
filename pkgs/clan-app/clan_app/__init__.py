import logging
import sys

# Remove working directory from sys.path
if "" in sys.path:
    sys.path.remove("")

from clan_cli.profiler import profile

from clan_app.app import MainApplication

log = logging.getLogger(__name__)


@profile
def main(argv: list[str] = sys.argv) -> int:
    app = MainApplication()
    return app.run(argv)
