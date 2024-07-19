import time

from wayland import GtkProc


def test_open(app: GtkProc) -> None:
    time.sleep(0.5)
    assert app.poll() is None
