from pathlib import Path

from clan_lib.errors import ClanCmdError, CmdOut


def _cmd_out(msg: str | None) -> CmdOut:
    return CmdOut(
        stdout="",
        stderr="error: attribute 'foo' missing\n",
        env=None,
        cwd=Path.cwd(),
        command_list=["nix", "build", ".#foo"],
        returncode=1,
        msg=msg,
    )


def test_clan_cmd_error_fills_the_api_fields() -> None:
    """The API payload is built from msg, description and location.

    Leaving them empty renders every nix, ssh and git failure as a blank
    error in the API and the GUI.
    """
    cmd = _cmd_out("failed to copy closure to jon")
    error = ClanCmdError(cmd)

    assert error.msg == "failed to copy closure to jon"
    assert error.description == "error: attribute 'foo' missing"
    assert error.location == "nix"
    # the CLI renders __str__, which stays the full CmdOut report
    assert str(error) == str(cmd)


def test_clan_cmd_error_falls_back_to_the_exit_code() -> None:
    assert ClanCmdError(_cmd_out(None)).msg == "Command failed with exit code 1"
