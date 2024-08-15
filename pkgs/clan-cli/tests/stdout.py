from typing import Any

import pytest
from pytest import CaptureFixture


class CaptureOutput:
    def __init__(self, capsys: CaptureFixture) -> None:
        self.capsys = capsys

    def __enter__(self) -> "CaptureOutput":
        self.capsys.readouterr()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> bool:
        res = self.capsys.readouterr()
        self.out = res.out
        self.err = res.err


@pytest.fixture
def capture_output(capsys: CaptureFixture) -> CaptureOutput:
    return CaptureOutput(capsys)
