import json
from pathlib import Path

import pytest
from clan_lib.cmd import RunOpts, run
from clan_lib.nix import nix_shell
from clan_lib.ssh.host_key import HostKeyCheck
from clan_lib.ssh.remote import Remote

from clan_cli.ssh.deploy_info import DeployInfo, find_reachable_host


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
    deploy_info = DeployInfo.from_qr_code(img_path, HostKeyCheck.NONE)

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
    deploy_info = DeployInfo.from_json(json.loads(data), HostKeyCheck.NONE)

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
    deploy_info = DeployInfo.from_hostnames(
        ["172.19.1.2", host.ssh_url()], HostKeyCheck.NONE
    )

    assert deploy_info.addrs[0].address == "172.19.1.2"

    remote = find_reachable_host(deploy_info=deploy_info)

    assert remote is not None
    assert remote.ssh_url() == host.ssh_url()
