import logging
import sys

from clan_cli.profiler import profile

from clan_vm_manager.app import MainApplication

log = logging.getLogger(__name__)


@profile
def main() -> int:
    app = MainApplication()
    return app.run(sys.argv)
