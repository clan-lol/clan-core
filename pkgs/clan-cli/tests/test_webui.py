import os
import select
import shutil
import subprocess
import sys
from pathlib import Path

from ports import PortFunction


def test_start_server(unused_tcp_port: PortFunction, temporary_dir: Path) -> None:
    port = unused_tcp_port()

    fifo = temporary_dir / "fifo"
    os.mkfifo(fifo)
    notify_script = temporary_dir / "notify.sh"
    bash = shutil.which("bash")
    assert bash is not None
    notify_script.write_text(
        f"""#!{bash}
set -x
echo "1" > {fifo}
"""
    )
    notify_script.chmod(0o700)

    env = os.environ.copy()
    env["BROWSER"] = str(notify_script)
    with subprocess.Popen(
        [sys.executable, "-m", "clan_cli.webui", "--port", str(port)], env=env
    ) as p:
        try:
            with open(fifo) as f:
                r, _, _ = select.select([f], [], [], 10)
                assert f in r
                assert f.read().strip() == "1"
        finally:
            p.kill()
