import logging
import sys

from clan_cli.profiler import profile

from clan_vm_manager.app import MainApplication

log = logging.getLogger(__name__)


@profile
def main(argv: list[str] = sys.argv) -> int:
    app = MainApplication()
    return app.run(argv)
