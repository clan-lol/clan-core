import pytest
from helpers import cli
from stdout import CaptureOutput


def test_help(capture_output: CaptureOutput) -> None:
    with capture_output as output, pytest.raises(SystemExit):
        cli.run(["--help"])
    assert output.out.startswith("usage:")
