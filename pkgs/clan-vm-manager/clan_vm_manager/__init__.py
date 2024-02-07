import logging
import sys

from .app import MainApplication

log = logging.getLogger(__name__)


def main() -> None:
    app = MainApplication()
    return app.run(sys.argv)
