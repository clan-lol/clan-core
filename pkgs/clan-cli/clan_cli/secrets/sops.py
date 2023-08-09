import json
import os
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Iterator, Union

from .. import tty
from ..dirs import user_config_dir
from ..errors import ClanError
from ..nix import nix_shell
from .folders import sops_users_folder


class SopsKey:
    def __init__(self, pubkey: str, username: str) -> None:
        self.pubkey = pubkey
        self.username = username


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
    key = SopsKey(pub_key, username="")
    users_folder = sops_users_folder()

    # Check if the public key already exists for any user
    if users_folder.exists():
        for user in users_folder.iterdir():
            if not user.is_dir():
                continue
            if read_key(user) == pub_key:
                key.username = user.name
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
    write_key(users_folder / username, pub_key, False)

    key.username = username

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


@contextmanager
def sops_manifest(keys: list[str]) -> Iterator[Path]:
    with NamedTemporaryFile(delete=False, mode="w") as manifest:
        json.dump(
            dict(creation_rules=[dict(key_groups=[dict(age=keys)])]), manifest, indent=2
        )
        manifest.flush()
        yield Path(manifest.name)


def update_keys(secret_path: Path, keys: list[str]) -> None:
    with sops_manifest(keys) as manifest:
        cmd = nix_shell(
            ["sops"],
            [
                "sops",
                "--config",
                str(manifest),
                "updatekeys",
                "--yes",
                str(secret_path / "secret"),
            ],
        )
        subprocess.run(cmd, check=True)


def encrypt_file(
    secret_path: Path, content: Union[IO[str], str], keys: list[str]
) -> None:
    folder = secret_path.parent
    folder.mkdir(parents=True, exist_ok=True)

    # hopefully /tmp is written to an in-memory file to avoid leaking secrets
    with sops_manifest(keys) as manifest, NamedTemporaryFile(delete=False) as f:
        try:
            with open(f.name, "w") as fd:
                if isinstance(content, str):
                    fd.write(content)
                else:
                    shutil.copyfileobj(content, fd)
            # we pass an empty manifest to pick up existing configuration of the user
            args = ["sops", "--config", str(manifest)]
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


def decrypt_file(secret_path: Path) -> str:
    cmd = nix_shell(["sops"], ["sops", "--decrypt", str(secret_path)])
    res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
    return res.stdout


def write_key(path: Path, publickey: str, overwrite: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if not overwrite:
            flags |= os.O_EXCL
        fd = os.open(path / "key.json", flags)
    except FileExistsError:
        raise ClanError(f"{path.name} already exists in {path}")
    with os.fdopen(fd, "w") as f:
        json.dump({"publickey": publickey, "type": "age"}, f, indent=2)


def read_key(path: Path) -> str:
    with open(path / "key.json") as f:
        try:
            key = json.load(f)
        except json.JSONDecodeError as e:
            raise ClanError(f"Failed to decode {path.name}: {e}")
    if key["type"] != "age":
        raise ClanError(
            f"{path.name} is not an age key but {key['type']}. This is not supported"
        )
    publickey = key.get("publickey")
    if not publickey:
        raise ClanError(f"{path.name} does not contain a public key")
    return publickey
