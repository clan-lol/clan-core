import os
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO

from .. import tty
from ..dirs import user_config_dir
from ..nix import nix_shell
from .folders import add_key, read_key, sops_users_folder


class SopsKey:
    def __init__(self, pubkey: str) -> None:
        self.pubkey = pubkey


def get_public_key(privkey: str) -> str:
    cmd = nix_shell(["age"], ["age-keygen", "-y"])
    res = subprocess.run(
        cmd, input=privkey, check=True, stdout=subprocess.PIPE, text=True
    )
    return res.stdout.strip()


def get_unique_user(users_folder: Path, user: str) -> str:
    """Return a unique path in the users_folder for the given user."""
    i = 0
    path = users_folder / user
    while path.exists():
        i += 1
        user = user + str(i)
        path = users_folder / user
    return user


def get_user_name(user: str) -> str:
    """Ask the user for their name until a unique one is provided."""
    while True:
        name = input(
            f"Enter your user name for which your sops key will be stored in the repository [default: {user}]: "
        )
        if name:
            user = name
        if not (sops_users_folder() / user).exists():
            return user
        print(f"{sops_users_folder() / user} already exists")


def ensure_user(pub_key: str) -> SopsKey:
    key = SopsKey(pub_key)
    users_folder = sops_users_folder()

    # Check if the public key already exists for any user
    if users_folder.exists():
        for user in users_folder.iterdir():
            if not user.is_dir():
                continue
            if read_key(user) == pub_key:
                return key

    # Find a unique user name if the public key is not found
    try:
        loginname = os.getlogin()
    except OSError:
        loginname = os.environ.get("USER", "nobody")
    username = get_unique_user(users_folder, loginname)

    if tty.is_interactive():
        # Ask the user for their name until a unique one is provided
        username = get_user_name(username)

    # Add the public key for the user
    add_key(users_folder / username, pub_key, False)

    return key


def ensure_sops_key() -> SopsKey:
    key = os.environ.get("SOPS_AGE_KEY")
    if key:
        return ensure_user(get_public_key(key))
    raw_path = os.environ.get("SOPS_AGE_KEY_FILE")
    if raw_path:
        path = Path(raw_path)
    else:
        path = user_config_dir() / "sops" / "age" / "keys.txt"
    if path.exists():
        return ensure_user(get_public_key(path.read_text()))
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = nix_shell(["age"], ["age-keygen", "-o", str(path)])
    subprocess.run(cmd, check=True)

    tty.info(
        f"Generated age key at '{path}'. Please back it up on a secure location or you will lose access to your secrets."
    )
    return ensure_user(get_public_key(path.read_text()))


def encrypt_file(secret_path: Path, content: IO[str], keys: list[str]) -> None:
    folder = secret_path.parent
    folder.mkdir(parents=True, exist_ok=True)

    # hopefully /tmp is written to an in-memory file to avoid leaking secrets
    with NamedTemporaryFile(delete=False) as f:
        try:
            with open(f.name, "w") as fd:
                shutil.copyfileobj(content, fd)
            args = ["sops"]
            for key in keys:
                args.extend(["--age", key])
            args.extend(["-i", "--encrypt", str(f.name)])
            cmd = nix_shell(["sops"], args)
            subprocess.run(cmd, check=True)
            # atomic copy of the encrypted file
            with NamedTemporaryFile(dir=folder, delete=False) as f2:
                shutil.copyfile(f.name, f2.name)
                os.rename(f2.name, secret_path)
        finally:
            try:
                os.remove(f.name)
            except OSError:
                pass
