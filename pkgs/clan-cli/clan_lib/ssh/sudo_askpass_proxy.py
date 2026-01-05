import logging
import shlex
import subprocess
import sys

# to get the the current tty state
import termios
import threading
from pathlib import Path
from typing import Protocol

from clan_lib.cmd import terminate_process
from clan_lib.errors import ClanError

logger = logging.getLogger(__name__)

remote_script = (Path(__file__).parent / "sudo_askpass_proxy.sh").read_text()


class RemoteP(Protocol):
    @property
    def address(self) -> str: ...

    @property
    def target(self) -> str: ...

    def ssh_cmd(self) -> list[str]: ...


class SudoAskpassProxy:
    def __init__(self, host: "RemoteP", prompt_command: list[str]) -> None:
        self.host = host
        self.password_prompt_command = prompt_command
        self.ssh_process: subprocess.Popen | None = None
        self.thread: threading.Thread | None = None

    def handle_password_request(self, prompt: str) -> str:
        """Get password from local user"""
        try:
            # Run the password prompt command
            password_command = [
                arg.replace("%title%", prompt) for arg in self.password_prompt_command
            ]
            old_settings = None
            if sys.stdin.isatty():
                # If stdin is a tty, we can safely change terminal settings
                old_settings = termios.tcgetattr(sys.stdin.fileno())
            try:
                logger.debug(
                    f"Running password prompt command: {' '.join(password_command)}",
                )
                password_process = subprocess.run(
                    password_command,
                    text=True,
                    check=False,
                    stdout=subprocess.PIPE,
                )
            finally:  # dialog messes with the terminal settings, so we need to restore them
                if old_settings is not None:
                    termios.tcsetattr(
                        sys.stdin.fileno(),
                        termios.TCSADRAIN,
                        old_settings,
                    )

            if password_process.returncode != 0:
                return "CANCELED"
            return password_process.stdout.strip()
        except ClanError as e:
            msg = f"Error running password prompt command: {e}"
            raise ClanError(msg) from e

    def _process(self, ssh_process: subprocess.Popen) -> None:
        """Execute the remote command with password proxying"""
        # Monitor SSH output for password requests
        if ssh_process.stdout is None:
            msg = "SSH process stdout is None"
            raise ClanError(msg)
        try:
            for line in ssh_process.stdout:
                stripped_line = line.strip()
                if stripped_line.startswith("PASSWORD_REQUESTED:"):
                    prompt = stripped_line[len("PASSWORD_REQUESTED:") :].strip()
                    password = self.handle_password_request(prompt)
                    if ssh_process.stdin is None:
                        logger.error("SSH process stdin is None")
                        return
                    print(password, file=ssh_process.stdin)
                    ssh_process.stdin.flush()
                else:
                    print(stripped_line)
        except (OSError, ClanError):
            logger.exception("Error processing passwords requests output")

    def run(self) -> str:
        """Run the SSH command with password proxying. Returns the askpass script path."""
        # Create a shell script to run on the remote host

        # Start SSH process
        # Force bash execution to handle users with non-bash default shells (e.g., fish)
        # Use shlex.quote to properly escape the script for the remote shell
        cmd = [*self.host.ssh_cmd(), "bash", "-c", shlex.quote(remote_script)]
        try:
            self.ssh_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
            )
        except OSError as e:
            msg = f"error connecting to {self.host.target}: {e}"
            raise ClanError(msg) from e

        # Monitor SSH output for password requests
        if self.ssh_process.stdout is None:
            msg = "SSH process stdout is None"
            raise ClanError(msg)

        for line in self.ssh_process.stdout:
            stripped_line = line.strip()
            if stripped_line.startswith("ASKPASS_SCRIPT:"):
                askpass_script = stripped_line[len("ASKPASS_SCRIPT:") :].strip()
                break
        else:
            msg = f"Failed to create askpass script on {self.host.target}. Did not receive ASKPASS_SCRIPT line."
            raise ClanError(msg)

        self.thread = threading.Thread(
            target=self._process,
            name="SudoAskpassProxy",
            args=(self.ssh_process,),
        )
        self.thread.start()
        return askpass_script

    def cleanup(self) -> None:
        """Terminate SSH process if still running"""
        if self.ssh_process:
            with terminate_process(self.ssh_process):
                pass

            # Unclear why we have to close this manually, but pytest reports unclosed fd
            if self.ssh_process.stdout is not None:
                self.ssh_process.stdout.close()
            if self.ssh_process.stdin is not None:
                self.ssh_process.stdin.close()
            self.ssh_process = None
        if self.thread:
            self.thread.join()
