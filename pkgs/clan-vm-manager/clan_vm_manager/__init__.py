import logging
import sys

from clan_cli.profiler import profile

from clan_vm_manager.app import MainApplication

log = logging.getLogger(__name__)
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

import time

@profile
def main(argv: list[str] = sys.argv) -> int:

    # Attempt to get the default display
    display = Gdk.Display.get_default()

    while display is None:
        log.info("Display not available yet. Retrying...")

        # Re-attempt initialization after a delay
        time.sleep(1)

        # Attempt to get the default display
        display = Gdk.Display.get_default()


    app = MainApplication()
    return app.run(argv)
