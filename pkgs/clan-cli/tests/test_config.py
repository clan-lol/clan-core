import json
from pathlib import Path
from typing import Any

import pytest

from clan_cli import config

base_args = [
    "",
    f"{Path(config.__file__).parent}/jsonschema/example-schema.json",
]


# use pytest.parametrize
@pytest.mark.parametrize(
    "args,expected",
    [
        (["name", "DavHau"], {"name": "DavHau"}),
        (
            ["kernelModules", "foo", "bar", "baz"],
            {"kernelModules": ["foo", "bar", "baz"]},
        ),
        (["services.opt", "test"], {"services": {"opt": "test"}}),
        (["userIds.DavHau", "42"], {"userIds": {"DavHau": 42}}),
    ],
)
def test_set_some_option(
    args: list[str],
    expected: dict[str, Any],
    capsys: pytest.CaptureFixture,
) -> None:
    config.main(base_args + args)
    captured = capsys.readout()
    json_out = json.loads(captured.out)
    assert json_out == expected
