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


def run_vm_in_thread(machine_name: str) -> None:
    # runs machine and prints exceptions
    def run() -> None:
        try:
            Cli().run(["vms", "run", machine_name])
        except Exception:
            # print exception details
            print(traceback.format_exc(), file=sys.stderr)
            print(sys.exc_info()[2], file=sys.stderr)

    # run the machine in a separate thread
    t = threading.Thread(target=run, name="run")
    t.daemon = True
    t.start()


# wait for qmp socket to exist
def wait_vm_up(state_dir: Path) -> None:
    socket_file = state_dir / "qga.sock"
    timeout: float = 120
    while True:
        if timeout <= 0:
            raise TimeoutError(
                f"qga socket {socket_file} not found. Is the VM running?"
            )
        if socket_file.exists():
            break
        sleep(0.1)
        timeout -= 0.1


# wait for vm to be down by checking if qga socket is down
def wait_vm_down(state_dir: Path) -> None:
    socket_file = state_dir / "qga.sock"
    timeout: float = 300
    while socket_file.exists():
        if timeout <= 0:
            raise TimeoutError(
                f"qga socket {socket_file} still exists. Is the VM down?"
            )
        sleep(0.1)
        timeout -= 0.1


# wait for vm to be up then connect and return qmp instance
def qmp_connect(state_dir: Path) -> QEMUMonitorProtocol:
    wait_vm_up(state_dir)
    qmp = QEMUMonitorProtocol(
        address=str(os.path.realpath(state_dir / "qmp.sock")),
    )
    qmp.connect()
    return qmp


# wait for vm to be up then connect and return qga instance
def qga_connect(state_dir: Path) -> QgaSession:
    wait_vm_up(state_dir)
    return QgaSession(os.path.realpath(state_dir / "qga.sock"))


@pytest.mark.impure
def test_inspect(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(["vms", "inspect", "--flake", str(test_flake_with_core.path), "vm1"])
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
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "admins",
            "user1",
        ]
    )
    cli.run(["vms", "run", "vm1"])


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_vm_qmp(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
) -> None:
    # set up a simple clan flake
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "new-clan",
        machine_configs=dict(
            my_machine=dict(
                clan=dict(
                    virtualisation=dict(graphics=False),
                    networking=dict(targetHost="client"),
                ),
                services=dict(getty=dict(autologinUser="root")),
            )
        ),
    )

    # 'clan vms run' must be executed from within the flake
    monkeypatch.chdir(flake.path)

    # the state dir is a point of reference for qemu interactions as it links to the qga/qmp sockets
    state_dir = vm_state_dir(str(flake.path), "my_machine")

    # start the VM
    run_vm_in_thread("my_machine")

    # connect with qmp
    qmp = qmp_connect(state_dir)

    # verify that issuing a command works
    # result = qmp.cmd_obj({"execute": "query-status"})
    result = qmp.command("query-status")
    assert result["status"] == "running", result

    # shutdown machine (prevent zombie qemu processes)
    qmp.command("system_powerdown")


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_vm_persistence(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
) -> None:
    # set up a clan flake with some systemd services to test persistence
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "new-clan",
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
                # create test user to test if state can be owned by user
                users=dict(
                    users=dict(
                        test=dict(
                            password="test",
                            isNormalUser=True,
                        ),
                        root=dict(password="root"),
                    )
                ),
                # create a systemd service to create a file in the state folder
                # and another to read it after reboot
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
                clan=dict(
                    virtualisation=dict(graphics=False),
                    networking=dict(targetHost="client"),
                ),
            )
        ),
    )
    monkeypatch.chdir(flake.path)

    # the state dir is a point of reference for qemu interactions as it links to the qga/qmp sockets
    state_dir = vm_state_dir(str(flake.path), "my_machine")

    run_vm_in_thread("my_machine")

    # wait for the VM to start
    wait_vm_up(state_dir)

    # wait for socket to be down (systemd service 'poweroff' rebooting machine)
    wait_vm_down(state_dir)

    # start vm again
    run_vm_in_thread("my_machine")

    # connect second time
    qga = qga_connect(state_dir)

    # ensure that the file created by the service is still there and has the expected content
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
    assert exitcode == 0, out

    # use qmp to shutdown the machine (prevent zombie qemu processes)
    qmp = qmp_connect(state_dir)
    qmp.command("system_powerdown")
