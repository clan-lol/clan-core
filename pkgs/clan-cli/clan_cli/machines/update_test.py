import os
from itertools import pairwise
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.update import _build_darwin_rebuild_cmd

from clan_cli.machines.update import (
    _remote_from_cli_override,
    get_machines_for_update,
    run_update_with_network,
)
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli


@pytest.mark.parametrize(
    ("test_flake_with_core", "explicit_names", "filter_tags", "expected_names"),
    [
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            ["jon"],  # explicit names
            [],  # filter tags
            ["jon"],  # expected
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_single_name(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


@pytest.mark.parametrize(
    ("test_flake_with_core", "explicit_names", "filter_tags", "expected_names"),
    [
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            [],  # explicit names
            ["foo"],  # filter tags
            ["jon", "sara"],  # expected
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_tags(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


@pytest.mark.parametrize(
    ("test_flake_with_core", "explicit_names", "filter_tags", "expected_names"),
    [
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            ["sara"],  # explicit names
            ["foo"],  # filter tags
            ["sara"],  # expected
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_tags_and_name(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


@pytest.mark.parametrize(
    ("test_flake_with_core", "explicit_names", "filter_tags", "expected_names"),
    [
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            [],  # no explicit names
            [],  # no filter tags
            ["jon", "sara", "vm1", "vm2"],  # all machines
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_implicit_all(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


def test_update_command_no_flake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["machines", "update", "machine1"])


@pytest.mark.parametrize("forward_agent", [False, True])
def test_remote_from_cli_override_forwards_agent(forward_agent: bool) -> None:
    machine = MagicMock()
    machine.name = "test-machine"
    machine.get_forward_agent.return_value = forward_agent
    remote = MagicMock()
    overridden_remote = MagicMock()
    remote.override.return_value = overridden_remote

    with patch(
        "clan_cli.machines.update.Remote.from_ssh_uri",
        return_value=remote,
    ) as from_ssh_uri:
        result = _remote_from_cli_override(
            machine=machine,
            address="root@build-host",
            host_key_check="strict",
        )

    from_ssh_uri.assert_called_once_with(
        machine_name="test-machine",
        address="root@build-host",
    )
    remote.override.assert_called_once_with(
        host_key_check="strict",
        forward_agent=forward_agent,
    )
    assert result is overridden_remote


def test_darwin_rebuild_cmd_no_literal_quotes() -> None:
    """Regression: flake fragment must not contain literal quotes.

    Literal quotes around the machine name (e.g. ``#"emily"``) cause
    darwin-rebuild to fail because Nix cannot resolve the quoted attribute path.
    """
    cmd = _build_darwin_rebuild_cmd(
        machine_name="emily",
        flake_store_path="/nix/store/abc123-source",
        nix_options=["--show-trace"],
    )

    flake_arg = cmd[cmd.index("--flake") + 1]

    assert flake_arg == "/nix/store/abc123-source#emily"
    assert '"' not in flake_arg
    assert "'" not in flake_arg


def test_darwin_rebuild_cmd_structure() -> None:
    """The returned command has the expected shape."""
    cmd = _build_darwin_rebuild_cmd(
        machine_name="my-mac",
        flake_store_path="/nix/store/xyz-source",
        nix_options=["-L", "--option", "keep-going", "true"],
    )

    assert cmd[0] == "/run/current-system/sw/bin/darwin-rebuild"
    assert cmd[1] == "switch"
    assert "-L" in cmd
    assert cmd[-2] == "--flake"
    assert cmd[-1] == "/nix/store/xyz-source#my-mac"


# TODO: Add more tests for requireExplicitUpdate


_FAKE_CONFIG_PATH = "/nix/store/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-fake-config"
_FAKE_FLAKE_PATH = "/nix/store/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb-fake-flake"


def _make_machine(machine_class: str, name: str = "test-machine") -> MagicMock:
    machine = MagicMock()
    machine.name = name
    machine._class_ = machine_class
    machine.flake.is_local = True
    machine.flake.path = "/fake/flake"
    return machine


def _run_result(returncode: int = 0, stdout: str = "", stderr: str = "") -> MagicMock:
    r = MagicMock()
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


def _setup_host_chain(
    mock_remote_cls: MagicMock,
) -> MagicMock:
    """Wire up Remote.from_ssh_uri → host_connection() → become_root() chain.

    Returns the ``target_host_root`` mock so callers can configure ``.run``.
    """
    mock_remote = MagicMock()
    mock_remote_cls.from_ssh_uri.return_value = mock_remote
    mock_remote.override.return_value = mock_remote

    mock_target_host = MagicMock()
    mock_remote.host_connection.return_value.__enter__.return_value = mock_target_host
    mock_remote.host_connection.return_value.__exit__.return_value = False

    mock_target_host_root = MagicMock()
    mock_target_host.become_root.return_value.__enter__.return_value = (
        mock_target_host_root
    )
    mock_target_host.become_root.return_value.__exit__.return_value = False

    return mock_target_host_root


def test_run_update_with_network_darwin_raises_on_specialisation() -> None:
    """Darwin with specialisation set must raise ClanError mentioning 'not supported for darwin'."""
    machine = _make_machine("darwin", name="my-mac")

    with pytest.raises(ClanError, match="not supported for darwin"):
        run_update_with_network(
            machine=machine,
            build_host=None,
            upload_inputs=False,
            host_key_check="none",
            target_host_override="root@192.0.2.1",
            specialisation="my-spec",
        )


@pytest.mark.parametrize(
    ("specialisation", "expected_switch_path"),
    [
        (
            None,
            f"{_FAKE_CONFIG_PATH}/bin/switch-to-configuration",
        ),
        (
            "my-spec",
            f"{_FAKE_CONFIG_PATH}/specialisation/my-spec/bin/switch-to-configuration",
        ),
    ],
)
def test_run_update_with_network_nixos_systemd_run_path(
    specialisation: str | None,
    expected_switch_path: str,
) -> None:
    """systemd-run calls must embed the correct config/specialisation path.

    The new activate flow runs two systemd-run invocations:
    1. switch-to-configuration boot  (register in bootloader)
    2. switch-to-configuration switch (live-activate)
    Both must use the correct binary path.
    """
    machine = _make_machine("nixos")

    with (
        patch("clan_cli.machines.update.Remote") as mock_remote_cls,
        patch("clan_lib.machines.update.upload_secret_vars"),
        patch(
            "clan_lib.machines.update.nix_metadata",
            return_value={"path": _FAKE_FLAKE_PATH},
        ),
        patch("clan_lib.machines.update._nixos_build", return_value=_FAKE_CONFIG_PATH),
        patch("clan_lib.machines.update.is_async_cancelled", return_value=False),
    ):
        mock_target_host_root = _setup_host_chain(mock_remote_cls)
        mock_target_host_root.run.return_value = _run_result(0)

        run_update_with_network(
            machine=machine,
            build_host=None,
            upload_inputs=False,
            host_key_check="none",
            target_host_override="root@192.0.2.1",
            specialisation=specialisation,
        )

    # Find all systemd-run calls among target_host_root.run invocations.
    systemd_run_calls = [
        c
        for c in mock_target_host_root.run.call_args_list
        if isinstance(c.args[0], list) and c.args[0][0] == "systemd-run"
    ]
    assert len(systemd_run_calls) >= 2, (
        "expected at least 2 systemd-run calls (boot + switch), "
        f"got {len(systemd_run_calls)}"
    )

    # First call: switch-to-configuration boot
    boot_cmd: list[str] = systemd_run_calls[0].args[0]
    assert boot_cmd[-2] == expected_switch_path
    assert boot_cmd[-1] == "boot"

    # Second call: switch-to-configuration switch
    switch_cmd: list[str] = systemd_run_calls[1].args[0]
    assert switch_cmd[-2] == expected_switch_path
    assert switch_cmd[-1] == "switch"


def test_nixos_activate_inhibitor_failure_suggests_reboot() -> None:
    """When switch fails due to switch inhibitors, error must suggest reboot.

    Boot must succeed, switch must fail with inhibitor output, and the
    resulting ClanError must mention reboot.
    """
    machine = _make_machine("nixos")

    def fake_run(cmd: object, _opts: object = None) -> MagicMock:
        if isinstance(cmd, list) and cmd[0] == "systemd-run":
            action = cmd[-1]
            if action == "boot":
                return _run_result(0)
            if action == "switch":
                return _run_result(
                    1,
                    stdout=(
                        "Checking switch inhibitors...\n"
                        "Pre-switch check 'switchInhibitors' failed\n"
                        "Pre-switch checks failed\n"
                    ),
                )
        # Default: succeed (test -e, nix-env, readlink, etc.)
        return _run_result(0)

    with (
        patch("clan_cli.machines.update.Remote") as mock_remote_cls,
        patch("clan_lib.machines.update.upload_secret_vars"),
        patch(
            "clan_lib.machines.update.nix_metadata",
            return_value={"path": _FAKE_FLAKE_PATH},
        ),
        patch("clan_lib.machines.update._nixos_build", return_value=_FAKE_CONFIG_PATH),
        patch("clan_lib.machines.update.is_async_cancelled", return_value=False),
    ):
        mock_target_host_root = _setup_host_chain(mock_remote_cls)
        mock_target_host_root.run.side_effect = fake_run

        with pytest.raises(ClanError, match=r"(?s)reboot.*--no-check"):
            run_update_with_network(
                machine=machine,
                build_host=None,
                upload_inputs=False,
                host_key_check="none",
                target_host_override="root@192.0.2.1",
            )

    # Verify: boot was called, but no retry after inhibitor failure.
    systemd_run_calls = [
        c
        for c in mock_target_host_root.run.call_args_list
        if isinstance(c.args[0], list) and c.args[0][0] == "systemd-run"
    ]
    actions = [c.args[0][-1] for c in systemd_run_calls]
    assert actions == ["boot", "switch"], (
        f"Expected exactly boot + switch (no retry), got {actions}"
    )


def test_nixos_activate_forwards_nixos_no_check() -> None:
    """NIXOS_NO_CHECK=1 in local env must be forwarded as KEY=VALUE via -E."""
    machine = _make_machine("nixos")

    with (
        patch("clan_cli.machines.update.Remote") as mock_remote_cls,
        patch("clan_lib.machines.update.upload_secret_vars"),
        patch(
            "clan_lib.machines.update.nix_metadata",
            return_value={"path": _FAKE_FLAKE_PATH},
        ),
        patch("clan_lib.machines.update._nixos_build", return_value=_FAKE_CONFIG_PATH),
        patch("clan_lib.machines.update.is_async_cancelled", return_value=False),
        patch.dict("os.environ", {"NIXOS_NO_CHECK": "1"}),
    ):
        mock_target_host_root = _setup_host_chain(mock_remote_cls)
        mock_target_host_root.run.return_value = _run_result(0)

        run_update_with_network(
            machine=machine,
            build_host=None,
            upload_inputs=False,
            host_key_check="none",
            target_host_override="root@192.0.2.1",
        )

    systemd_run_calls = [
        c
        for c in mock_target_host_root.run.call_args_list
        if isinstance(c.args[0], list) and c.args[0][0] == "systemd-run"
    ]
    for call in systemd_run_calls:
        cmd: list[str] = call.args[0]
        # -E NIXOS_NO_CHECK=1 must appear as consecutive elements
        pairs = list(pairwise(cmd))
        assert ("-E", "NIXOS_NO_CHECK=1") in pairs, (
            f"NIXOS_NO_CHECK=1 not forwarded in: {cmd}"
        )


def test_nixos_activate_omits_nixos_no_check_when_unset() -> None:
    """When NIXOS_NO_CHECK is not in the environment, it must not appear in the command."""
    machine = _make_machine("nixos")

    # Ensure NIXOS_NO_CHECK is NOT set
    env_without = {k: v for k, v in os.environ.items() if k != "NIXOS_NO_CHECK"}

    with (
        patch("clan_cli.machines.update.Remote") as mock_remote_cls,
        patch("clan_lib.machines.update.upload_secret_vars"),
        patch(
            "clan_lib.machines.update.nix_metadata",
            return_value={"path": _FAKE_FLAKE_PATH},
        ),
        patch("clan_lib.machines.update._nixos_build", return_value=_FAKE_CONFIG_PATH),
        patch("clan_lib.machines.update.is_async_cancelled", return_value=False),
        patch.dict("os.environ", env_without, clear=True),
    ):
        mock_target_host_root = _setup_host_chain(mock_remote_cls)
        mock_target_host_root.run.return_value = _run_result(0)

        run_update_with_network(
            machine=machine,
            build_host=None,
            upload_inputs=False,
            host_key_check="none",
            target_host_override="root@192.0.2.1",
        )

    systemd_run_calls = [
        c
        for c in mock_target_host_root.run.call_args_list
        if isinstance(c.args[0], list) and c.args[0][0] == "systemd-run"
    ]
    for call in systemd_run_calls:
        cmd_str = " ".join(call.args[0])
        assert "NIXOS_NO_CHECK" not in cmd_str, (
            f"NIXOS_NO_CHECK should not appear when unset: {call.args[0]}"
        )
