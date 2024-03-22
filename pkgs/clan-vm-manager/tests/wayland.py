from collections.abc import Generator
from subprocess import Popen

import pytest


@pytest.fixture(scope="session")
def wayland_compositor() -> Generator[Popen, None, None]:
    # Start the Wayland compositor (e.g., Weston)
    compositor = Popen(["weston", "--backend=headless-backend.so"])
    yield compositor
    # Cleanup: Terminate the compositor
    compositor.terminate()


@pytest.fixture(scope="function")
def gtk_app(wayland_compositor: Popen) -> Generator[Popen, None, None]:
    # Assuming your GTK4 app can be started via a command line
    # It's important to ensure it uses the Wayland session initiated by the fixture
    env = {"GDK_BACKEND": "wayland"}
    app = Popen(["clan-vm-manager"], env=env)
    yield app
    # Cleanup: Terminate your application
    app.terminate()
