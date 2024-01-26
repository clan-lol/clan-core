import base64
import json
import os
import socket
import threading
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest, generate_flake
from root import CLAN_CORE

from clan_cli.dirs import vm_state_dir

if TYPE_CHECKING:
    from age_keys import KeyPair

no_kvm = not os.path.exists("/dev/kvm")


# qga is almost like qmp, but not quite, because:
#   - server doesn't send initial message
#   - no need to initialize by asking for capabilities
#   - results need to be base64 decoded
# TODO: move this to an extra file and make it available to other parts like GUI
class QgaSession:
    def __init__(self, socket_file: Path | str) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # try to reconnect a couple of times if connetion refused
        for _ in range(100):
            try:
                self.sock.connect(str(socket_file))
                return
            except ConnectionRefusedError:
                sleep(0.1)
        self.sock.connect(str(socket_file))

    def get_response(self) -> dict:
        result = self.sock.recv(9999999)
        return json.loads(result)

    # only execute, don't wait for response
    def exec_cmd(self, cmd: str) -> None:
        self.sock.send(
            json.dumps(
                {
                    "execute": "guest-exec",
                    "arguments": {
                        "path": "/bin/sh",
                        "arg": ["-l", "-c", cmd],
                        "capture-output": True,
                    },
                }
            ).encode("utf-8")
        )

    # run, wait for result, return exitcode and output
    def run(self, cmd: str) -> tuple[int, str]:
        self.exec_cmd(cmd)
        result_pid = self.get_response()
        pid = result_pid["return"]["pid"]
        # loop until exited=true
        status_payload = json.dumps(
            {
                "execute": "guest-exec-status",
                "arguments": {
                    "pid": pid,
                },
            }
        ).encode("utf-8")
        while True:
            self.sock.send(status_payload)
            result = self.get_response()
            if "error" in result and result["error"]["desc"].startswith("PID"):
                raise Exception("PID could not be found")
            if result["return"]["exited"]:
                break
            sleep(0.1)

        exitcode = result["return"]["exitcode"]
        if exitcode == 0:
            out = (
                ""
                if "out-data" not in result["return"]
                else base64.b64decode(result["return"]["out-data"]).decode("utf-8")
            )
        else:
            out = (
                ""
                if "err-data" not in result["return"]
                else base64.b64decode(result["return"]["err-data"]).decode("utf-8")
            )
        return exitcode, out


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
                                "/var/my-state"
                                # to be owned by user 'test'
                                "/var/user-state"
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
                                    reboot
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
                                fi

                                # ensure /var/user-state is owned by test
                                # if [ "$(stat -c '%U' /var/user-state)" != "test" ]; then
                                #     echo "state folder /var/user-state is not owned by user test" > /var/my-state/error
                                # fi

                            """,
                            serviceConfig=dict(
                                Type="oneshot",
                            ),
                        ),
                        # TODO: implement shutdown via qmp instead of this hack
                        poweroff=dict(
                            description="Poweroff the machine",
                            wantedBy=["multi-user.target"],
                            after=["read_after_reboot.service"],
                            script="""
                                sleep 5
                                poweroff
                            """,
                        ),
                    )
                ),
                clan=dict(virtualisation=dict(graphics=False)),
            )
        ),
    )
    monkeypatch.chdir(flake.path)

    # run the machine in a separate thread
    def run() -> None:
        Cli().run(["vms", "run", "my_machine"])

    t = threading.Thread(target=run, name="run")
    t.daemon = True
    t.start()

    state_dir = vm_state_dir("_test_vm_persistence", str(flake.path), "my_machine")

    # wait until socket file exists
    while True:
        if (state_dir / "qga.sock").exists():
            break
        sleep(0.1)
    qga = QgaSession(os.path.realpath(str(state_dir / "qga.sock")))
    # wait for the machine to reboot
    while True:
        try:
            # this might crash as the operation is not atomic
            exitcode, out = qga.run("cat /var/my-state/rebooted")
            if exitcode == 0:
                break
        except Exception:
            pass
        finally:
            sleep(0.1)

    # ensure that /etc get persisted (required to persist user IDs)
    exitcode, out = qga.run("ls /vmstate/.rw-etc/upper")
    assert exitcode == 0, out

    exitcode, out = qga.run("cat /var/my-state/test")
    assert exitcode == 0, out
    assert out == "dream2nix\n", out

    # check for errors
    exitcode, out = qga.run("cat /var/my-state/error")
    assert exitcode == 1, out
