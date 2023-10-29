import os
import select
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from cli import Cli
from ports import PortFunction


@pytest.mark.timeout(10)
def test_start_server(unused_tcp_port: PortFunction, temporary_home: Path) -> None:
    Cli()
    port = unused_tcp_port()

    fifo = temporary_home / "fifo"
    os.mkfifo(fifo)

    # Create a script called "firefox" in the temporary home directory that
    # writes "1" to the fifo. This is used to notify the test that the firefox has been
    # started.
    notify_script = temporary_home / "firefox"
    bash = shutil.which("bash")
    assert bash is not None
    notify_script.write_text(
        f"""#!{bash}
set -x
echo "1" > {fifo}
"""
    )
    notify_script.chmod(0o700)

    # Add the temporary home directory to the PATH so that the script is found
    env = os.environ.copy()
    env["PATH"] = f"{temporary_home}:{env['PATH']}"

    # Add build/src to PYTHONPATH so that the webui module is found in nix sandbox
    # TODO: We need a way to make sure things which work in the devshell also work in the sandbox
    python_path = env.get("PYTHONPATH")
    if python_path:
        env["PYTHONPATH"] = f"/build/src:{python_path}"

    # breakpoint_container(
    #     cmd=[sys.executable, "-m", "clan_cli.webui", "--port", str(port)],
    #     env=env,
    #     work_dir=temporary_home,
    # )

    with subprocess.Popen(
        [sys.executable, "-m", "clan_cli.webui", "--port", str(port)],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
        text=True,
    ) as p:
        try:
            with open(fifo) as f:
                r, _, _ = select.select([f], [], [], 10)
                assert f in r
                assert f.read().strip() == "1"
        finally:
            p.kill()
