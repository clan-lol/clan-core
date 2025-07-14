import json
from pathlib import Path

import pytest
from clan_lib.cmd import RunOpts, run
from clan_lib.nix import nix_shell
from clan_lib.ssh.remote import Remote

from clan_cli.ssh.deploy_info import DeployInfo, find_reachable_host
from clan_cli.tests.fixtures_flakes import ClanFlake
from clan_cli.tests.helpers import cli


def test_qrcode_scan(temp_dir: Path) -> None:
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
    deploy_info = DeployInfo.from_qr_code(img_path, "none")

    host = deploy_info.addrs[0]
    assert host.address == "192.168.122.86"
    assert host.user == "root"
    assert host.password == "scabbed-defender-headlock"

    tor_host = deploy_info.addrs[1]
    assert (
        tor_host.address
        == "qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion"
    )
    assert tor_host.tor_socks is True
    assert tor_host.password == "scabbed-defender-headlock"
    assert tor_host.user == "root"
    assert (
        tor_host.address
        == "qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion"
    )


def test_from_json() -> None:
    data = '{"pass":"scabbed-defender-headlock","tor":"qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion","addrs":["192.168.122.86"]}'
    deploy_info = DeployInfo.from_json(json.loads(data), "none")

    host = deploy_info.addrs[0]
    assert host.password == "scabbed-defender-headlock"
    assert host.address == "192.168.122.86"

    tor_host = deploy_info.addrs[1]
    assert (
        tor_host.address
        == "qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion"
    )
    assert tor_host.tor_socks is True
    assert tor_host.password == "scabbed-defender-headlock"
    assert tor_host.user == "root"
    assert (
        tor_host.address
        == "qjeerm4r6t55hcfum4pinnvscn5njlw2g3k7ilqfuu7cdt3ahaxhsbid.onion"
    )


@pytest.mark.with_core
def test_find_reachable_host(hosts: list[Remote]) -> None:
    host = hosts[0]

    uris = ["172.19.1.2", host.ssh_url()]
    remotes = [Remote.from_ssh_uri(machine_name="some", address=uri) for uri in uris]
    deploy_info = DeployInfo(addrs=remotes)

    assert deploy_info.addrs[0].address == "172.19.1.2"

    remote = find_reachable_host(deploy_info=deploy_info)

    assert remote is not None
    assert remote.ssh_url() == host.ssh_url()


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
