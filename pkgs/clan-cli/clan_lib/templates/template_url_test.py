from pathlib import Path

import pytest

from clan_lib.errors import ClanError
from clan_lib.templates.template_url import transform_url

template_type = "machine"


class DummyFlake:
    def __init__(self, path: str) -> None:
        self.path: Path = Path(path)

    def get_input_names(self) -> list[str]:
        return ["locked-input"]


local_path = DummyFlake(".")


def test_transform_url_self_explizit_dot() -> None:
    user_input = ".#new-machine"
    expected_selector = 'clan.templates.machine."new-machine"'

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_transform_url_self_no_dot() -> None:
    user_input = "#new-machine"
    expected_selector = 'clan.templates.machine."new-machine"'

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_transform_url_builtin_template() -> None:
    user_input = "new-machine"
    expected_selector = 'clanInternals.templates.machine."new-machine"'

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_transform_url_remote_template() -> None:
    user_input = "github:/org/repo#new-machine"
    expected_selector = 'clan.templates.machine."new-machine"'

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)

    assert flake_ref == "github:/org/repo"
    assert selector == expected_selector


def test_transform_url_explicit_path() -> None:
    user_input = ".#clan.templates.machine.new-machine"
    expected_selector = "clan.templates.machine.new-machine"

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


# Currently quoted selectors are treated as explicit paths.
def test_transform_url_quoted_selector() -> None:
    user_input = '.#"new.machine"'
    expected_selector = '"new.machine"'
    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_single_quote_selector() -> None:
    user_input = ".#'new.machine'"
    expected_selector = "'new.machine'"
    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_custom_template_path() -> None:
    user_input = "github:/org/repo#my.templates.custom.machine"
    expected_selector = "my.templates.custom.machine"

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == "github:/org/repo"
    assert selector == expected_selector


def test_full_url_query_and_fragment() -> None:
    user_input = "github:/org/repo?query=param#my.templates.custom.machine"
    expected_flake_ref = "github:/org/repo?query=param"
    expected_selector = "my.templates.custom.machine"

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == expected_flake_ref
    assert selector == expected_selector


def test_custom_template_type() -> None:
    user_input = "#my.templates.custom.machine"
    expected_selector = "my.templates.custom.machine"

    flake_ref, selector = transform_url("custom", user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_malformed_identifier() -> None:
    user_input = "github:/org/repo#my.templates.custom.machine#extra"
    with pytest.raises(ClanError) as exc_info:
        _flake_ref, _selector = transform_url(
            template_type, user_input, flake=local_path
        )

    assert isinstance(exc_info.value, ClanError)
    assert (
        str(exc_info.value)
        == "Invalid template identifier: More than one '#' found. Please use a single '#'"
    )


def test_locked_input_template() -> None:
    user_input = "locked-input#new-machine"
    expected_selector = 'inputs.locked-input.clan.templates.machine."new-machine"'

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert flake_ref == str(local_path.path)
    assert selector == expected_selector


def test_locked_input_template_no_quotes() -> None:
    user_input = 'locked-input#"new.machine"'
    expected_selector = 'inputs.locked-input."new.machine"'

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert selector == expected_selector
    assert flake_ref == str(local_path.path)


def test_locked_input_template_no_dot() -> None:
    user_input = "locked-input#new.machine"
    expected_selector = "inputs.locked-input.new.machine"

    flake_ref, selector = transform_url(template_type, user_input, flake=local_path)
    assert selector == expected_selector
    assert flake_ref == str(local_path.path)
