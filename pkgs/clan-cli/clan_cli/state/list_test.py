import pytest

from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


@pytest.mark.with_core
@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        {
            "inventory_expr": r"""{
                instances.zerotier = {
                    module.name = "zerotier";
                    roles.controller.machines.vm1 = {};
                    roles.peer.machines.vm2 = {};
                };
            }""",
        },
    ],
    indirect=True,
)
def test_state_list_vm1(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(["state", "list", "vm1", "--flake", str(test_flake_with_core.path)])
    assert output.out is not None
    assert "service: zerotier" in output.out
    assert "/var/lib/zerotier-one" in output.out


@pytest.mark.with_core
@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        {
            "inventory_expr": r"""{
                instances.zerotier = {
                    module.name = "zerotier";
                    roles.controller.machines.vm1 = {};
                    roles.peer.machines.vm2 = {};
                };
            }""",
        },
    ],
    indirect=True,
)
def test_state_list_vm2(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(["state", "list", "vm2", "--flake", str(test_flake_with_core.path)])
    assert output.out is not None
    # Peers have no state folders, only the controller does
    assert "service: zerotier" not in output.out
