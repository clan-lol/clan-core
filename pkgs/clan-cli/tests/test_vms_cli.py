import os
import sys
import threading
import traceback
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest, generate_flake
from root import CLAN_CORE

from clan_cli.dirs import vm_state_dir
from clan_cli.qemu.qga import QgaSession
from clan_cli.qemu.qmp import QEMUMonitorProtocol

if TYPE_CHECKING:
    from age_keys import KeyPair

no_kvm = not os.path.exists("/dev/kvm")


@pytest.mark.impure
def test_inspect(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(["--flake", str(test_flake_with_core.path), "vms", "inspect", "vm1"])
    out = capsys.readouterr()  # empty the buffer
    assert "Cores" in out.out


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_run(
    monkeypatch: pytest.MonkeyPatch,
    test_flake_with_core: FlakeForTest,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.chdir(test_flake_with_core.path)
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    cli = Cli()
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(["vms", "run", "vm1"])


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_vm_persistence(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "new-clan",
        substitutions={
            "__CHANGE_ME__": "_test_vm_persistence",
            "git+https://git.clan.lol/clan/clan-core": "path://" + str(CLAN_CORE),
        },
        machine_configs=dict(
            my_machine=dict(
                services=dict(getty=dict(autologinUser="root")),
                clanCore=dict(
                    state=dict(
                        my_state=dict(
                            folders=[
                                # to be owned by root
                                "/var/my-state",
                                # to be owned by user 'test'
                                "/var/user-state",
                            ]
                        )
                    )
                ),
                # create test user
                # TODO: test persisting files via that user
                users=dict(
                    users=dict(
                        test=dict(
                            password="test",
                            isNormalUser=True,
                        ),
                        root=dict(password="root"),
                    )
                ),
                systemd=dict(
                    services=dict(
                        create_state=dict(
                            description="Create a file in the state folder",
                            wantedBy=["multi-user.target"],
                            script="""
                                if [ ! -f /var/my-state/root ]; then
                                    echo "Creating a file in the state folder"
                                    echo "dream2nix" > /var/my-state/root
                                    # create /var/my-state/test owned by user test
                                    echo "dream2nix" > /var/my-state/test
                                    chown test /var/my-state/test
                                    # make sure /var/user-state is owned by test
                                    chown test /var/user-state
                                fi
                            """,
                            serviceConfig=dict(
                                Type="oneshot",
                            ),
                        ),
                        reboot=dict(
                            description="Reboot the machine",
                            wantedBy=["multi-user.target"],
                            after=["my-state.service"],
                            script="""
                                if [ ! -f /var/my-state/rebooting ]; then
                                    echo "Rebooting the machine"
                                    touch /var/my-state/rebooting
                                    poweroff
                                else
                                    touch /var/my-state/rebooted
                                fi
                            """,
                        ),
                        read_after_reboot=dict(
                            description="Read a file in the state folder",
                            wantedBy=["multi-user.target"],
                            after=["reboot.service"],
                            # TODO: currently state folders itself cannot be owned by users
                            script="""
                                if ! cat /var/my-state/test; then
                                    echo "cannot read from state file" > /var/my-state/error
                                # ensure root file is owned by root
                                elif [ "$(stat -c '%U' /var/my-state/root)" != "root" ]; then
                                    echo "state file /var/my-state/root is not owned by user root" > /var/my-state/error
                                # ensure test file is owned by test
                                elif [ "$(stat -c '%U' /var/my-state/test)" != "test" ]; then
                                    echo "state file /var/my-state/test is not owned by user test" > /var/my-state/error
                                # ensure /var/user-state is owned by test
                                elif [ "$(stat -c '%U' /var/user-state)" != "test" ]; then
                                    echo "state folder /var/user-state is not owned by user test" > /var/my-state/error
                                fi

                            """,
                            serviceConfig=dict(
                                Type="oneshot",
                            ),
                        ),
                    )
                ),
                clan=dict(virtualisation=dict(graphics=False)),
            )
        ),
    )
    monkeypatch.chdir(flake.path)

    state_dir = vm_state_dir("_test_vm_persistence", str(flake.path), "my_machine")
    socket_file = state_dir / "qga.sock"

    # wait until socket file exists
    def connect() -> QgaSession:
        while True:
            if (state_dir / "qga.sock").exists():
                break
            sleep(0.1)
        return QgaSession(os.path.realpath(socket_file))

    # runs machine and prints exceptions
    def run() -> None:
        try:
            Cli().run(["vms", "run", "my_machine"])
        except Exception:
            # print exception details
            print(traceback.format_exc())
            print(sys.exc_info()[2])

    # run the machine in a separate thread
    t = threading.Thread(target=run, name="run")
    t.daemon = True
    t.start()

    # wait for socket to be up
    Path("/tmp/log").write_text(f"wait for socket to be up: {socket_file!s}")
    while True:
        if socket_file.exists():
            break
        sleep(0.1)

    # wait for socket to be down (systemd service 'poweroff' rebooting machine)
    Path("/tmp/log").write_text("wait for socket to be down")
    while socket_file.exists():
        sleep(0.1)
    Path("/tmp/log").write_text("socket is down")

    # start vm again
    t = threading.Thread(target=run, name="run")
    t.daemon = True
    t.start()

    # wait for the socket to be up
    Path("/tmp/log").write_text("wait for socket to be up second time")
    while True:
        if socket_file.exists():
            break
        sleep(0.1)

    # connect second time
    Path("/tmp/log").write_text("connecting")
    qga = connect()

    # ensure that either /var/lib/nixos or /etc gets persisted
    # (depending on if system.etc.overlay.enable is set or not)
    exitcode, out, err = qga.run(
        "ls /vmstate/var/lib/nixos/gid-map || ls /vmstate/.rw-etc/upper"
    )
    assert exitcode == 0, err

    exitcode, out, err = qga.run("cat /var/my-state/test")
    assert exitcode == 0, err
    assert out == "dream2nix\n", out

    # check for errors
    exitcode, out, err = qga.run("cat /var/my-state/error")
    assert exitcode == 1, out

    # check all systemd services are OK, or print details
    exitcode, out, err = qga.run(
        "systemctl --failed | tee /tmp/yolo | grep -q '0 loaded units listed' || ( cat /tmp/yolo && false )"
    )
    print(out)
    assert exitcode == 0, out

    qmp = QEMUMonitorProtocol(
        address=str(os.path.realpath(state_dir / "qmp.sock")),
    )
    qmp.connect()
    qmp.cmd_obj({"execute": "system_powerdown"})
