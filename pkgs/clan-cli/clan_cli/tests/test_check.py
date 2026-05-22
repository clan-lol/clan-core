import json
from collections.abc import Callable

import pytest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput
from clan_lib.errors import ClanError
from clan_lib.flake import Flake


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_passes(
    clan_flake: Callable[..., Flake],
) -> None:
    """Clan check exits 0 when all constraints are satisfied."""
    flake = clan_flake(
        raw=r"""
        {
          modules."test-svc" = {
            _class = "clan.service";
            manifest.name = "test-svc";
            manifest.constraints.maxInstances = 1;
            roles.default = {};
          };
          inventory.machines.m1 = {};
          inventory.instances."only-one" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
        }
        """
    )

    cli.run(["check", "--flake", str(flake.path)])


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_fails_max_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    """Clan check exits 1 when maxInstances is violated."""
    flake = clan_flake(
        raw=r"""
        {
          modules."test-svc" = {
            _class = "clan.service";
            manifest.name = "test-svc";
            manifest.constraints.maxInstances = 1;
            roles.default = {};
          };
          inventory.machines.m1 = {};
          inventory.instances."inst-a" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
          inventory.instances."inst-b" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
        }
        """
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.run(["check", "--flake", str(flake.path)])

    assert exc_info.value.code == 1


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_fails_min_machines(
    clan_flake: Callable[..., Flake],
) -> None:
    """Clan check exits 1 when minMachines is violated."""
    flake = clan_flake(
        raw=r"""
        {
          modules."test-svc" = {
            _class = "clan.service";
            manifest.name = "test-svc";
            manifest.constraints.roles.server.minMachines = 1;
            roles.server = {};
            roles.default = {};
          };
          inventory.machines.m1 = {};
          inventory.instances."my-svc" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
        }
        """
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.run(["check", "--flake", str(flake.path)])

    assert exc_info.value.code == 1


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_json_output(
    clan_flake: Callable[..., Flake],
    capture_output: CaptureOutput,
) -> None:
    """Clan check --json emits structured check results."""
    flake = clan_flake(
        raw=r"""
        {
          modules."test-svc" = {
            _class = "clan.service";
            manifest.name = "test-svc";
            manifest.constraints.maxInstances = 1;
            roles.default = {};
          };
          inventory.machines.m1 = {};
          inventory.instances."inst-a" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
          inventory.instances."inst-b" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
        }
        """
    )

    with capture_output as output, pytest.raises(SystemExit):
        cli.run(["check", "--json", "--flake", str(flake.path)])

    checks = json.loads(output.out)
    assert isinstance(checks, list)
    assert len(checks) == 1
    assert checks[0]["severity"] == "error"
    assert checks[0]["id"] == "test-svc-maxInstances"
    assert "at most 1" in checks[0]["message"]


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_json_empty_when_passing(
    clan_flake: Callable[..., Flake],
    capture_output: CaptureOutput,
) -> None:
    """Clan check --json emits an empty list when no violations exist."""
    flake = clan_flake(
        raw=r"""
        {
          modules."test-svc" = {
            _class = "clan.service";
            manifest.name = "test-svc";
            manifest.constraints.maxInstances = 1;
            roles.default = {};
          };
          inventory.machines.m1 = {};
          inventory.instances."only-one" = {
            module.name = "test-svc";
            module.input = "self";
            roles.default.machines.m1 = {};
          };
        }
        """
    )

    with capture_output as output:
        cli.run(["check", "--json", "--flake", str(flake.path)])

    checks = json.loads(output.out)
    assert checks == []


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_role_max_machines_exceeded(
    clan_flake: Callable[..., Flake],
    capture_output: CaptureOutput,
) -> None:
    """5 machines on a moon role capped at 4 triggers an error."""
    flake = clan_flake(
        raw=r"""
        {
          modules."mynet" = {
            _class = "clan.service";
            manifest.name = "mynet";
            manifest.constraints.roles.moon.maxMachines = 4;
            roles.moon = {};
          };
          inventory.machines.m1 = {};
          inventory.machines.m2 = {};
          inventory.machines.m3 = {};
          inventory.machines.m4 = {};
          inventory.machines.m5 = {};
          inventory.instances."vpn" = {
            module.name = "mynet";
            module.input = "self";
            roles.moon.machines.m1 = {};
            roles.moon.machines.m2 = {};
            roles.moon.machines.m3 = {};
            roles.moon.machines.m4 = {};
            roles.moon.machines.m5 = {};
          };
        }
        """
    )

    with capture_output as output, pytest.raises(SystemExit) as exc_info:
        cli.run(["check", "--json", "--flake", str(flake.path)])

    assert exc_info.value.code == 1
    checks = json.loads(output.out)
    assert len(checks) == 1
    assert checks[0]["id"] == "mynet-vpn-moon-maxMachines"
    assert checks[0]["severity"] == "error"
    assert "at most 4" in checks[0]["message"]
    assert "5 are assigned" in checks[0]["message"]


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_check_role_max_machines_at_cap(
    clan_flake: Callable[..., Flake],
) -> None:
    """Exactly 4 machines on a moon role capped at 4 passes."""
    flake = clan_flake(
        raw=r"""
        {
          modules."mynet" = {
            _class = "clan.service";
            manifest.name = "mynet";
            manifest.constraints.roles.moon.maxMachines = 4;
            roles.moon = {};
          };
          inventory.machines.m1 = {};
          inventory.machines.m2 = {};
          inventory.machines.m3 = {};
          inventory.machines.m4 = {};
          inventory.instances."vpn" = {
            module.name = "mynet";
            module.input = "self";
            roles.moon.machines.m1 = {};
            roles.moon.machines.m2 = {};
            roles.moon.machines.m3 = {};
            roles.moon.machines.m4 = {};
          };
        }
        """
    )

    cli.run(["check", "--flake", str(flake.path)])


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_vars_generate_blocked_by_check_errors(
    clan_flake: Callable[..., Flake],
) -> None:
    """Vars generate refuses to run when inventory checks have errors."""
    flake = clan_flake(
        raw=r"""
        {
          modules."mynet" = {
            _class = "clan.service";
            manifest.name = "mynet";
            manifest.constraints.roles.moon.maxMachines = 4;
            roles.moon = {};
          };
          inventory.machines.m1 = {};
          inventory.machines.m2 = {};
          inventory.machines.m3 = {};
          inventory.machines.m4 = {};
          inventory.machines.m5 = {};
          inventory.instances."vpn" = {
            module.name = "mynet";
            module.input = "self";
            roles.moon.machines.m1 = {};
            roles.moon.machines.m2 = {};
            roles.moon.machines.m3 = {};
            roles.moon.machines.m4 = {};
            roles.moon.machines.m5 = {};
          };
        }
        """
    )

    with pytest.raises(ClanError, match="Inventory checks failed"):
        cli.run(["vars", "generate", "--flake", str(flake.path)])
