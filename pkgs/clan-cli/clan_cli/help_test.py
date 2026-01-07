import argparse

from clan_cli.help import HelpFormatter


def test_help_formatter_adds_default_to_choices() -> None:
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "toml"],
        default="json",
        help="Output format",
    )

    format_action = next(a for a in parser._actions if "--format" in a.option_strings)
    formatter = HelpFormatter(prog="test")
    help_string = formatter._get_help_string(format_action)

    assert "(default: json)" in help_string, (
        "default value not added to choice argument"
    )
    assert "Output format" in help_string, "original help text not preserved"


def test_help_formatter_no_default_for_non_choices() -> None:
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument(
        "--name",
        default="test",
        help="Name of the thing",
    )

    name_action = next(a for a in parser._actions if "--name" in a.option_strings)
    formatter = HelpFormatter(prog="test")
    help_string = formatter._get_help_string(name_action)

    assert "(default:" not in help_string, (
        "default value incorrectly added to non-choice argument"
    )
    assert "Name of the thing" in help_string, "original help text not preserved"


def test_help_formatter_no_default_when_none() -> None:
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "toml"],
        default=None,
        help="Output format",
    )

    format_action = next(a for a in parser._actions if "--format" in a.option_strings)
    formatter = HelpFormatter(prog="test")
    help_string = formatter._get_help_string(format_action)

    assert "(default:" not in help_string, (
        "default value incorrectly added when default is None"
    )
    assert "Output format" in help_string, "original help text not preserved"


def test_help_formatter_preserves_existing_default_marker() -> None:
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "toml"],
        default="json",
        help="Output format (default: %(default)s)",
    )

    format_action = next(a for a in parser._actions if "--format" in a.option_strings)
    formatter = HelpFormatter(prog="test")
    help_string = formatter._get_help_string(format_action)

    assert "%(default)s" in help_string, "existing %(default)s placeholder removed"
    assert help_string.count("(default:") == 1, (
        "default value duplicated when %(default)s already present"
    )
