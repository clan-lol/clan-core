import logging
from dataclasses import dataclass
from pathlib import Path

from clan_lib.api import API
from clan_lib.cmd import Log, RunOpts, run
from clan_lib.dirs import user_nixos_anywhere_dir

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SSHKeyPair:
    private: Path
    public: Path


@API.register
def create_nixos_anywhere_ssh_key() -> SSHKeyPair:
    """
    Create a new SSH key pair for NixOS Anywhere.
    The keys are stored in ~/.config/clan/nixos-anywhere/keys/id_ed25519 and id_ed25519.pub.
    """
    private_key_dir = user_nixos_anywhere_dir()

    key_pair = generate_ssh_key(private_key_dir)

    return key_pair


def generate_ssh_key(root_dir: Path) -> SSHKeyPair:
    """
    Generate a new SSH key pair at root_dir/keys/id_ed25519 and id_ed25519.pub.
    If the key already exists, it will not be regenerated.
    """
    key_dir = root_dir / "keys"
    key_dir.mkdir(parents=True, exist_ok=True)
    key_dir.chmod(0o700)
    priv_key = key_dir / "id_ed25519"

    keypair = SSHKeyPair(
        private=priv_key,
        public=key_dir / "id_ed25519.pub",
    )

    if priv_key.exists():
        return keypair

    log.info(f"Generating nixos-anywhere SSH key pair at {priv_key}")
    cmd = [
        "ssh-keygen",
        "-N",
        "",
        "-t",
        "ed25519",
        "-f",
        str(priv_key),
    ]
    run(cmd, RunOpts(log=Log.BOTH))

    return keypair
