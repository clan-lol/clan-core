import json
from pathlib import Path

import pytest
from clan_lib.cmd import RunOpts, run
from clan_lib.flake import Flake
from clan_lib.network.qr_code import read_qr_image, read_qr_json
from clan_lib.nix import nix_shell
from clan_lib.ssh.remote import Remote

from clan_cli.tests.fixtures_flakes import ClanFlake
from clan_cli.tests.helpers import cli


@pytest.mark.with_core
def test_qrcode_scan(temp_dir: Path, flake: ClanFlake) -> None:
    data = '{"pass":"scabbed-defender-headlock","tor":"qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion","addrs":["192.168.122.86"]}'
    img_path = temp_dir / "qrcode.png"
    cmd = nix_shell(
        ["qrencode"],
        [
            "qrencode",
            "-o",
            str(img_path),
        ],
    )
    run(cmd, RunOpts(input=data.encode()))

    # Call the qrcode_scan function
    json_data = read_qr_image(img_path)
    qr_code = read_qr_json(json_data, Flake(str(flake.path)))

    # Check addresses
    addresses = qr_code.addresses
    assert len(addresses) >= 2  # At least direct and tor

    # Find direct connection
    direct_remote = None
    for addr in addresses:
        if addr.network.module_name == "clan_lib.network.direct":
            direct_remote = addr.remote
            break

    assert direct_remote is not None
    assert direct_remote.address == "192.168.122.86"
    assert direct_remote.user == "root"
    assert direct_remote.password == "scabbed-defender-headlock"

    # Find tor connection
    tor_remote = None
    for addr in addresses:
        if addr.network.module_name == "clan_lib.network.tor":
            tor_remote = addr.remote
            break

    assert tor_remote is not None
    assert (
        tor_remote.address
        == "qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion"
    )
    assert tor_remote.socks_port == 9050
    assert tor_remote.password == "scabbed-defender-headlock"
    assert tor_remote.user == "root"


def test_from_json(temp_dir: Path) -> None:
    data = '{"pass":"scabbed-defender-headlock","tor":"qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion","addrs":["192.168.122.86"]}'
    flake = Flake(str(temp_dir))
    qr_code = read_qr_json(json.loads(data), flake)

    # Check addresses
    addresses = qr_code.addresses
    assert len(addresses) >= 2  # At least direct and tor

    # Find direct connection
    direct_remote = None
    for addr in addresses:
        if addr.network.module_name == "clan_lib.network.direct":
            direct_remote = addr.remote
            break

    assert direct_remote is not None
    assert direct_remote.password == "scabbed-defender-headlock"
    assert direct_remote.address == "192.168.122.86"

    # Find tor connection
    tor_remote = None
    for addr in addresses:
        if addr.network.module_name == "clan_lib.network.tor":
            tor_remote = addr.remote
            break

    assert tor_remote is not None
    assert (
        tor_remote.address
        == "qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion"
    )
    assert tor_remote.socks_port == 9050
    assert tor_remote.password == "scabbed-defender-headlock"
    assert tor_remote.user == "root"


# TODO: This test needs to be updated to use get_best_remote from clan_lib.network.network
# @pytest.mark.with_core
# def test_find_reachable_host(hosts: list[Remote]) -> None:
#     host = hosts[0]
#
#     uris = ["172.19.1.2", host.ssh_url()]
#     remotes = [Remote.from_ssh_uri(machine_name="some", address=uri) for uri in uris]
#
#     assert remotes[0].address == "172.19.1.2"
#
#     remote = find_reachable_host(remotes=remotes)
#
#     assert remote is not None
#     assert remote.ssh_url() == host.ssh_url()


@pytest.mark.with_core
def test_ssh_shell_from_deploy(
    hosts: list[Remote],
    flake: ClanFlake,
) -> None:
    host = hosts[0]

    machine1_config = flake.machines["m1_machine"]
    machine1_config["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    machine1_config["clan"]["networking"]["targetHost"] = host.ssh_url()
    flake.refresh()

    assert host.private_key

    success_txt = flake.path / "success.txt"
    assert not success_txt.exists()
    cli.run(
        [
            "ssh",
            "--flake",
            str(flake.path),
            "m1_machine",
            "--host-key-check=none",
            "--ssh-option",
            "IdentityFile",
            str(host.private_key),
            "--remote-command",
            "touch",
            str(success_txt),
            "&&",
            "exit 0",
        ]
    )

    assert success_txt.exists()
