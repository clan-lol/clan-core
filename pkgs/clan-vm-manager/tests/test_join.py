import time

from wayland import GtkApp


def test_open(app: GtkApp) -> None:
    while app.poll() is None:
        time.sleep(0.1)
    assert True
