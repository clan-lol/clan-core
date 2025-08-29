from collections.abc import Callable

import pytest
from clan_cli.tests.fixtures_flakes import nested_dict
from clan_lib.flake.flake import Flake
from clan_lib.services.modules import list_service_instances


@pytest.mark.with_core
def test_list_service_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    config = nested_dict()
    config["inventory"]["machines"]["alice"] = {}
    config["inventory"]["machines"]["bob"] = {}
    # implicit module selection (defaults to clan-core/admin)
    config["inventory"]["instances"]["admin"]["roles"]["default"]["tags"]["all"] = {}
    # explicit module selection
    config["inventory"]["instances"]["my-sshd"]["module"]["input"] = "clan-core"
    config["inventory"]["instances"]["my-sshd"]["module"]["name"] = "sshd"
    # input = null
    config["inventory"]["instances"]["my-sshd-2"]["module"]["input"] = None
    config["inventory"]["instances"]["my-sshd-2"]["module"]["name"] = "sshd"
    # external input
    flake = clan_flake(config)

    instances = list_service_instances(flake)

    assert list(instances.keys()) == ["admin", "my-sshd", "my-sshd-2"]
    assert instances["admin"]["module"]["module"].get("input") == "clan-core"
    assert instances["admin"]["module"]["module"].get("name") == "admin"
    assert instances["my-sshd"]["module"]["module"].get("input") == "clan-core"
    assert instances["my-sshd"]["module"]["module"].get("name") == "sshd"
    assert instances["my-sshd-2"]["module"]["module"].get("input") == "clan-core"
    assert instances["my-sshd-2"]["module"]["module"].get("name") == "sshd"
