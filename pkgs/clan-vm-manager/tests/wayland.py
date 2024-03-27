# Import necessary modules
import os
import shlex
import subprocess
import sys
import time
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

# Assuming NewType is already imported or defined somewhere
import pytest


def write_script(cmd: list[str], new_env: dict[str, str], name:str) -> None:
    # Create the bash script content
    script_content = "#!/bin/bash\n"
    for key, value in new_env.items():
        if '"' in value:
            value = value.replace('"', '\\"')
        if "'" in value:
            value = value.replace("'", "\\'")
        if '`' in value:
            value = value.replace("`", "\\`")
        script_content += f'export {key}="{value}"\n'
    script_content += shlex.join(cmd)

    # Write the bash script to a file
    script_filename = name
    with open(script_filename, "w") as script_file:
        script_file.write(script_content)

    print(f"You can find the script at {os.getcwd()}/{script_filename}")
    # Make the script executable
    os.chmod(script_filename, 0o755)


class Compositor:
    def __init__(self, proc: subprocess.Popen, env: dict[str, str]) -> None:
        self.proc = proc
        self.env = env

@pytest.fixture
def weston_override_lib(test_root: Path) ->  Generator[Path, None, None]:
    with TemporaryDirectory() as tmpdir:
        # This enforces a login shell by overriding the login shell of `getpwnam(3)`
        lib_path = Path(tmpdir) / "libweston_auth_override.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-o",
                lib_path,
                str(test_root / "weston_auth_override.c"),
            ],
            check=True,
        )
        yield lib_path


@pytest.fixture
def wayland_comp(test_root: Path, weston_override_lib: Path) -> Generator[Compositor, None, None]:
    tls_key = test_root / "data" / "rdp-security" / "tls.key"
    tls_cert = test_root / "data" / "rdp-security" / "tls.crt"
    wayland_display = "wayland-1"  # Define a unique WAYLAND_DISPLAY value
    new_env = os.environ.copy()
    new_env["WAYLAND_DISPLAY"] = wayland_display
    # Uncomment the next line if you need to force software rendering
    new_env["LIBGL_ALWAYS_SOFTWARE"] = "true"
    new_env["LD_PRELOAD"] = str(weston_override_lib)
    cmd = [
            "weston",
            "--width=1920",
            "--height=1080",
            "--port=5900",
            f"--vnc-tls-key={tls_key}",
            f"--vnc-tls-cert={tls_cert}",
            "--backend=vnc",
            f"--socket={wayland_display}",
        ]

    compositor = subprocess.Popen(
        cmd,
        env=new_env,
        text=True,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
    )
    time.sleep(0.4)
    if compositor.poll() is not None:
        raise Exception(f"Failed to start {cmd}")
    yield Compositor(compositor, new_env)
    compositor.kill()


class GtkApp:
    def __init__(self, proc: subprocess.Popen) -> None:
        self.proc = proc

    def kill(self) -> None:
        self.proc.kill()

    def wait(self) -> None:
        self.proc.wait()

    def poll(self) -> int | None:
        return self.proc.poll()

@pytest.fixture
def app(wayland_comp: Compositor) -> Generator[GtkApp, None, None]:
    # Define the new environment variables
    new_env = wayland_comp.env
    new_env["GDK_BACKEND"] = "wayland"

    # Define the command to be executed
    cmd = [f"{sys.executable}", "-m", "clan_vm_manager"]

    write_script(cmd, new_env, "weston.sh")
    breakpoint()

    # Execute the script
    rapp = subprocess.Popen(
        cmd,
        text=True,
        env=new_env,
        stdin=sys.stdin,
    )
    time.sleep(0.4)
    if rapp.poll() is not None:
        raise Exception(f"Failed to start {cmd}")
    yield GtkApp(rapp)
    rapp.kill()
