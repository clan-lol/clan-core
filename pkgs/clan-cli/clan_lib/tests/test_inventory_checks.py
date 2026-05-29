from collections.abc import Callable

import pytest

from clan_lib.flake import Flake
from clan_lib.inventory_checks import get_service_checks


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_collect_inventory_checks_empty_when_passing(
    clan_flake: Callable[..., Flake],
) -> None:
    """No violations => checks/errors/warnings are all empty."""
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

    result = get_service_checks(flake)

    assert result.checks == []
    assert result.errors == []
    assert result.warnings == []


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_collect_inventory_checks_reports_error(
    clan_flake: Callable[..., Flake],
) -> None:
    """Exceeding maxInstances surfaces as an error entry."""
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

    result = get_service_checks(flake)

    assert result.warnings == []
    assert len(result.errors) == 1
    assert result.errors == result.checks
    err = result.errors[0]
    assert err["id"] == "test-svc-maxInstances"
    assert err["severity"] == "error"
    assert "at most 1" in err["message"]


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_collect_inventory_checks_role_max_machines(
    clan_flake: Callable[..., Flake],
) -> None:
    """5 machines on a role capped at 4 yields a single error."""
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

    result = get_service_checks(flake)

    assert len(result.errors) == 1
    err = result.errors[0]
    assert err["id"] == "mynet-vpn-moon-maxMachines"
    assert err["severity"] == "error"
    assert "at most 4" in err["message"]
    assert "5 are assigned" in err["message"]


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_role_max_machines_passes_across_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    """maxMachines=1 on controller role passes when split across two instances."""
    flake = clan_flake(
        raw=r"""
        {
          modules."mynet" = {
            _class = "clan.service";
            manifest.name = "mynet";
            manifest.constraints.roles.controller.maxMachines = 1;
            roles.controller = {};
            roles.peer = {};
          };
          inventory.machines.m1 = {};
          inventory.machines.m2 = {};
          inventory.instances."net-a" = {
            module.name = "mynet";
            module.input = "self";
            roles.controller.machines.m1 = {};
            roles.peer.machines.m2 = {};
          };
          inventory.instances."net-b" = {
            module.name = "mynet";
            module.input = "self";
            roles.controller.machines.m2 = {};
            roles.peer.machines.m1 = {};
          };
        }
        """
    )

    result = get_service_checks(flake)

    assert result.errors == []
    assert result.warnings == []


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_role_min_machines_passes_across_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    """minMachines=1 on controller passes when both instances satisfy it."""
    flake = clan_flake(
        raw=r"""
        {
          modules."mynet" = {
            _class = "clan.service";
            manifest.name = "mynet";
            manifest.constraints.roles.controller.minMachines = 1;
            roles.controller = {};
            roles.peer = {};
          };
          inventory.machines.m1 = {};
          inventory.machines.m2 = {};
          inventory.instances."net-a" = {
            module.name = "mynet";
            module.input = "self";
            roles.controller.machines.m1 = {};
            roles.peer.machines.m2 = {};
          };
          inventory.instances."net-b" = {
            module.name = "mynet";
            module.input = "self";
            roles.controller.machines.m2 = {};
            roles.peer.machines.m1 = {};
          };
        }
        """
    )

    result = get_service_checks(flake)

    assert result.errors == []
    assert result.warnings == []


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_role_min_machines_fails_in_one_of_two_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    """minMachines=1 on controller errors for the instance that has none."""
    flake = clan_flake(
        raw=r"""
        {
          modules."mynet" = {
            _class = "clan.service";
            manifest.name = "mynet";
            manifest.constraints.roles.controller.minMachines = 1;
            roles.controller = {};
            roles.peer = {};
          };
          inventory.machines.m1 = {};
          inventory.machines.m2 = {};
          inventory.instances."net-a" = {
            module.name = "mynet";
            module.input = "self";
            roles.controller.machines.m1 = {};
            roles.peer.machines.m2 = {};
          };
          inventory.instances."net-b" = {
            module.name = "mynet";
            module.input = "self";
            roles.peer.machines.m1 = {};
          };
        }
        """
    )

    result = get_service_checks(flake)

    assert len(result.errors) == 1
    err = result.errors[0]
    assert err["id"] == "mynet-net-b-controller-minMachines"
    assert err["severity"] == "error"
    assert "at least 1" in err["message"]
    assert "0 are assigned" in err["message"]
