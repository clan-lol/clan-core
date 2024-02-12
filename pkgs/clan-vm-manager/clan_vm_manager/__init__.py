import logging
import sys

from .app import MainApplication

log = logging.getLogger(__name__)


# TODO: Trayicon support
# https://github.com/nicotine-plus/nicotine-plus/blob/b08552584eb6f35782ad77da93ae4aae3362bf64/pynicotine/gtkgui/widgets/trayicon.py#L982
def main() -> None:
    app = MainApplication()
    return app.run(sys.argv)
