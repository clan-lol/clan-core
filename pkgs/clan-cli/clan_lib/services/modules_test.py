from collections.abc import Callable

import pytest
from clan_cli.tests.fixtures_flakes import nested_dict
from clan_lib.flake.flake import Flake
from clan_lib.services.modules import list_service_instances, list_service_modules


@pytest.mark.with_core
def test_list_service_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    config = nested_dict()
    # explicit module selection
    # We use this random string in test to avoid code dependencies on the input name
    config["inventory"]["instances"]["foo"]["module"]["input"] = (
        "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"
    )
    config["inventory"]["instances"]["foo"]["module"]["name"] = "sshd"
    # input = null
    config["inventory"]["instances"]["bar"]["module"]["input"] = None
    config["inventory"]["instances"]["bar"]["module"]["name"] = "sshd"

    # Omit input
    config["inventory"]["instances"]["baz"]["module"]["name"] = "sshd"
    # external input
    flake = clan_flake(config)

    service_modules = list_service_modules(flake)

    assert len(service_modules.modules)
    assert any(m.usage_ref["name"] == "sshd" for m in service_modules.modules)

    instances = list_service_instances(flake)

    assert set(instances.keys()) == {"foo", "bar", "baz"}

    # Reference to a built-in module
    assert instances["foo"].resolved.usage_ref.get("input") is None
    assert instances["foo"].resolved.usage_ref.get("name") == "sshd"
    assert instances["foo"].resolved.info.manifest.name == "clan-core/sshd"
    # Actual module
    assert (
        instances["foo"].module.get("input")
        == "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"
    )

    # Module exposes the input name?
    assert instances["bar"].resolved.usage_ref.get("input") is None
    assert instances["bar"].resolved.usage_ref.get("name") == "sshd"

    assert instances["baz"].resolved.usage_ref.get("input") is None
    assert instances["baz"].resolved.usage_ref.get("name") == "sshd"
