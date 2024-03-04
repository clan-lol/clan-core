import logging
import sys

from clan_vm_manager.app import MainApplication
from clan_vm_manager.components.profiler import profile

log = logging.getLogger(__name__)


@profile
def main() -> int:
    app = MainApplication()
    return app.run(sys.argv)
