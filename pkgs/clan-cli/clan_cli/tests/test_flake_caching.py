import logging

import pytest
from clan_cli.flake import Flake, FlakeCache, FlakeCacheEntry
from clan_cli.tests.fixtures_flakes import ClanFlake

log = logging.getLogger(__name__)


def test_select() -> None:
    testdict = {"x": {"y": [123, 345, 456], "z": "bla"}}
    test_cache = FlakeCacheEntry(testdict, [])
    assert test_cache["x"]["z"].value == "bla"
    assert test_cache.is_cached(["x", "z"])
    assert not test_cache.is_cached(["x", "y", "z"])
    assert test_cache.select(["x", "y", 0]) == 123
    assert not test_cache.is_cached(["x", "z", 1])


def test_insert() -> None:
    test_cache = FlakeCacheEntry({}, [])
    # Inserting the same thing twice should succeed
    test_cache.insert(None, ["nix"])
    test_cache.insert(None, ["nix"])
    assert test_cache.select(["nix"]) is None


def test_out_path() -> None:
    testdict = {"x": {"y": [123, 345, 456], "z": "/nix/store/bla"}}
    test_cache = FlakeCacheEntry(testdict, [])
    assert test_cache.select(["x", "z"]) == "/nix/store/bla"
    assert test_cache.select(["x", "z", "outPath"]) == "/nix/store/bla"


@pytest.mark.with_core
def test_flake_caching(flake: ClanFlake) -> None:
    m1 = flake.machines["machine1"]
    m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    flake.machines["machine2"] = m1.copy()
    flake.machines["machine3"] = m1.copy()
    flake.refresh()

    flake_ = Flake(str(flake.path))
    hostnames = flake_.select("nixosConfigurations.*.config.networking.hostName")
    assert hostnames == {
        "machine1": "machine1",
        "machine2": "machine2",
        "machine3": "machine3",
    }


@pytest.mark.with_core
def test_cache_persistance(flake: ClanFlake) -> None:
    m1 = flake.machines["machine1"]
    m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    flake.refresh()

    flake1 = Flake(str(flake.path))
    flake2 = Flake(str(flake.path))
    flake1.prefetch()
    flake2.prefetch()
    assert isinstance(flake1._cache, FlakeCache)  # noqa: SLF001
    assert isinstance(flake2._cache, FlakeCache)  # noqa: SLF001
    assert not flake1._cache.is_cached(  # noqa: SLF001
        "nixosConfigurations.*.config.networking.hostName"
    )
    flake1.select("nixosConfigurations.*.config.networking.hostName")
    flake1.select("nixosConfigurations.*.config.networking.{hostName,hostId}")
    flake2.prefetch()
    assert flake2._cache.is_cached(  # noqa: SLF001
        "nixosConfigurations.*.config.networking.{hostName,hostId}"
    )


@pytest.mark.with_core
def test_conditional_all_selector(flake: ClanFlake) -> None:
    m1 = flake.machines["machine1"]
    m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    flake.refresh()

    flake1 = Flake(str(flake.path))
    flake2 = Flake(str(flake.path))
    flake1.prefetch()
    flake2.prefetch()
    assert isinstance(flake1._cache, FlakeCache)  # noqa: SLF001
    assert isinstance(flake2._cache, FlakeCache)  # noqa: SLF001
    log.info("First select")
    res1 = flake1.select("inputs.*.{clan,missing}")

    log.info("Second (cached) select")
    res2 = flake1.select("inputs.*.{clan,missing}")

    assert res1 == res2
    assert res1["clan-core"].get("clan") is not None

    flake2.prefetch()


# Test that the caching works
@pytest.mark.with_core
def test_caching_works(flake: ClanFlake) -> None:
    from unittest.mock import patch

    from clan_cli.flake import Flake

    my_flake = Flake(str(flake.path))

    with patch.object(
        my_flake, "get_from_nix", wraps=my_flake.get_from_nix
    ) as tracked_build:
        assert tracked_build.call_count == 0
        my_flake.select("clanInternals.inventory.meta")
        assert tracked_build.call_count == 1
        my_flake.select("clanInternals.inventory.meta")
        assert tracked_build.call_count == 1


# This test fails because the CI sandbox does not have the required packages to run the generators
# maybe @DavHau or @Qubasa can fix this at some point :)
# @pytest.mark.with_core
# def test_cache_invalidation(flake: ClanFlake, sops_setup: SopsSetup) -> None:
#     m1 = flake.machines["machine1"]
#     m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
#     flake.refresh()
#     clan_dir = Flake(str(flake.path))
#     machine1 = Machine(
#         name="machine1",
#         flake=clan_dir,
#     )
#     sops_setup.init(flake.path)
#     generate_vars([machine1])
#
#     flake.inventory["services"] = {
#         "sshd": {
#             "someid": {
#                 "roles": {
#                     "server": {
#                         "machines": ["machine1"],
#                     }
#                 }
#             }
#         }
#     }
#     flake.refresh()
#     machine1.flush_caches()  # because flake.refresh() does not invalidate the cache but it writes into the directory
#
#     generate_vars([machine1])
#     vpn_ip = (
#         get_var(str(clan_dir), machine1.name, "openssh/ssh.id_ed25519")
#         .value.decode()
#         .strip("\n")
#     )
#     assert vpn_ip is not None
