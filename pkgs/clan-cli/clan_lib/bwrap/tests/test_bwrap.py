import sys

import pytest
from clan_lib.bwrap import bubblewrap_works


@pytest.mark.skipif(sys.platform != "linux", reason="bubblewrap only works on linux")
def test_bubblewrap_works_on_linux() -> None:
    assert bubblewrap_works() is True
