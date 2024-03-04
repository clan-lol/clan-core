import logging
import sys

from clan_vm_manager.app import MainApplication

log = logging.getLogger(__name__)


def main() -> int:
    app = MainApplication()
    return app.run(sys.argv)
