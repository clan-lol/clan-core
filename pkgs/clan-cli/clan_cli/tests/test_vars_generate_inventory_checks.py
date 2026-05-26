from collections.abc import Callable

import pytest
from clan_cli.tests.helpers import cli
from clan_lib.errors import ClanError
from clan_lib.flake import Flake


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
