import dataclasses
import enum
import io
import json
import logging
import os
import re
import shutil
import subprocess
from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Any

from clan_lib.cmd import Log, RunOpts, run
from clan_lib.dirs import user_config_dir
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix import nix_shell

from .folders import sops_users_folder

AGE_RECIPIENT_REGEX = re.compile(r"^.*((age1|ssh-(rsa|ed25519) ).*?)(\s|$)")

log = logging.getLogger(__name__)


class KeyType(enum.Enum):
    AGE = enum.auto()
    PGP = enum.auto()

    def __str__(self) -> str:
        return self.name

    @classmethod
    def validate(cls, value: str | None) -> "KeyType | None":
        if value:
            return cls.__members__.get(value.upper())
        return None

    @property
    def sops_recipient_attr(self) -> str:
        """Name of the attribute to get the recipient key from a Sops file."""
        if self == self.AGE:
            return "recipient"
        if self == self.PGP:
            return "fp"
        msg = (
            f"KeyType is not properly implemented: "
            f'"sops_recipient_attr" is missing for key type "{self.name}"'
        )
        raise ClanError(msg)

    def collect_public_keys(self) -> list["SopsKey"]:
        keyring = []

        if self == self.AGE:

            def maybe_read_from_path(key_path: Path) -> None:
                try:
                    # as in parse.go in age:
                    content = Path(key_path).read_text().strip()

                    try:
                        for public_key in get_public_age_keys(content):
                            log.debug(
                                f"Found age public key from a private key "
                                f"in {key_path}: {public_key}",
                            )

                            keyring.append(
                                SopsKey(
                                    pubkey=public_key,
                                    username="",
                                    key_type=self,
                                    source=str(key_path),
                                ),
                            )
                    except ClanError as e:
                        error_msg = f"Failed to read age keys from {key_path}"
                        raise ClanError(error_msg) from e

                except FileNotFoundError:
                    return
                except OSError as ex:
                    log.warning(f"Could not read age keys from {key_path}", exc_info=ex)

            if keys := os.environ.get("SOPS_AGE_KEY"):
                # SOPS_AGE_KEY is fed into age.ParseIdentities by Sops, and
                # reads identities line by line. See age/keysource.go in
                # Sops, and age/parse.go in Age.
                content = keys.strip()

                try:
                    for public_key in get_public_age_keys(content):
                        log.debug(
                            f"Found age public key from a private key "
                            f"in the environment (SOPS_AGE_KEY): {public_key}",
                        )

                        keyring.append(
                            SopsKey(
                                pubkey=public_key,
                                username="",
                                key_type=self,
                                source="SOPS_AGE_KEY",
                            ),
                        )
                except ClanError as e:
                    error_msg = "Failed to read age keys from SOPS_AGE_KEY"
                    raise ClanError(error_msg) from e

            # Sops will try every location, see age/keysource.go
            elif key_path := os.environ.get("SOPS_AGE_KEY_FILE"):
                maybe_read_from_path(Path(key_path))
            else:
                maybe_read_from_path(user_config_dir() / "sops/age/keys.txt")

            return keyring

        if self == self.PGP:
            if pgp_fingerprints := os.environ.get("SOPS_PGP_FP"):
                for fp in pgp_fingerprints.strip().split(","):
                    msg = f"Found PGP public key in the environment (SOPS_PGP_FP): {fp}"
                    log.debug(msg)
                    keyring.append(
                        SopsKey(
                            pubkey=fp,
                            username="",
                            key_type=self,
                            source="SOPS_PGP_FP",
                        ),
                    )
            return keyring

        msg = f"KeyType {self.name.lower()} is missing an implementation for collect_public_keys"
        raise ClanError(msg)


@dataclasses.dataclass(frozen=True, order=True)
class SopsKey:
    pubkey: str
    # Two SopsKey are considered equal even
    # if they don't have the same username:
    username: str = dataclasses.field(compare=False)
    key_type: KeyType
    source: str = dataclasses.field(compare=False)

    def as_dict(self) -> dict[str, str]:
        return {
            "publickey": self.pubkey,
            "username": self.username,
            "type": self.key_type.name.lower(),
            "source": self.source,
        }

    def __str__(self) -> str:
        return f"({self.key_type.name}) {self.pubkey} (source: {self.source})"

    @classmethod
    def load_dir(cls, folder: Path) -> set["SopsKey"]:
        """Load from the file named `keys.json` in the given directory."""
        return read_keys(folder)

    @classmethod
    def collect_public_keys(cls) -> list["SopsKey"]:
        result = []
        for key_type in KeyType:
            result.extend(key_type.collect_public_keys())
        return result


class ExitStatus(enum.IntEnum):  # see: cmd/sops/codes/codes.go
    ERROR_GENERIC = 1
    COULD_NOT_READ_INPUT_FILE = 2
    COULD_NOT_WRITE_OUTPUT_FILE = 3
    ERROR_DUMPING_TREE = 4
    ERROR_READING_CONFIG = 5
    ERROR_INVALID_KMS_ENCRYPTION_CONTEXT_FORMAT = 6
    ERROR_INVALID_SET_FORMAT = 7
    ERROR_CONFLICTING_PARAMETERS = 8
    ERROR_ENCRYPTING_MAC = 21
    ERROR_ENCRYPTING_TREE = 23
    ERROR_DECRYPTING_MAC = 24
    ERROR_DECRYPTING_TREE = 25
    CANNOT_CHANGE_KEYS_FROM_NON_EXISTENT_FILE = 49
    MAC_MISMATCH = 51
    MAC_NOT_FOUND = 52
    CONFIG_FILE_NOT_FOUND = 61
    KEYBOARD_INTERRUPT = 85
    INVALID_TREE_PATH_FORMAT = 91
    NEED_AT_LEAST_ONE_DOCUMENT = 92
    NO_FILE_SPECIFIED = 100
    COULD_NOT_RETRIEVE_KEY = 128
    NO_ENCRYPTION_KEY_FOUND = 111
    DUPLICATE_DECRYPTION_KEY_TYPE = 112
    FILE_HAS_NOT_BEEN_MODIFIED = 200
    NO_EDITOR_FOUND = 201
    FAILED_TO_COMPARE_VERSIONS = 202
    FILE_ALREADY_ENCRYPTED = 203

    @classmethod
    def parse(cls, code: int) -> "ExitStatus | None":
        return ExitStatus(code) if code in ExitStatus else None


# class Executer(Protocol):
#     def __call__(
#         self, cmd: list[str], *, env: dict[str, str] | None = None
#     ) -> CmdOut: ...


class Operation(enum.StrEnum):
    DECRYPT = "decrypt"
    EDIT = "edit"
    ENCRYPT = "encrypt"
    UPDATE_KEYS = "updatekeys"


def load_age_plugins(flake: Flake) -> list[str]:
    result = flake.select("clanInternals.?secrets.?age.?plugins")
    plugins = result["secrets"]["age"]["plugins"]
    if plugins == {}:
        plugins = []

    if isinstance(plugins, list):
        return plugins

    msg = f"Expected a list of age plugins but {type(plugins)!r} was provided"
    raise ClanError(msg)


def sops_run(
    call: Operation,
    secret_path: Path,
    public_keys: Iterable[SopsKey],
    age_plugins: list[str] | None,
    run_opts: RunOpts | None = None,
) -> tuple[int, str]:
    """Call the sops binary for the given operation."""
    # louis(2024-11-19): I regrouped the call into the sops binary into this
    # one place because calling into sops needs to be done with a carefully
    # setup context, and I don't feel good about the idea of having that logic
    # exist in multiple places.
    if age_plugins is None:
        age_plugins = []
    sops_cmd = ["sops"]
    environ = os.environ.copy()
    with NamedTemporaryFile(delete=False, mode="w") as manifest:
        if call == Operation.DECRYPT:
            sops_cmd.append("decrypt")
        else:
            # When sops is used to edit a file the config is only used at
            # file creation, otherwise the keys from the existing file are
            # used.
            sops_cmd.extend(["--config", manifest.name])

            keys_by_type: dict[KeyType, list[str]] = {}
            keys_by_type = {key_type: [] for key_type in KeyType}
            for key in public_keys:
                keys_by_type[key.key_type].append(key.pubkey)
            it = keys_by_type.items()
            key_groups = [{key_type.name.lower(): keys for key_type, keys in it}]
            rules = {"creation_rules": [{"key_groups": key_groups}]}
            json.dump(rules, manifest, indent=2)
            manifest.flush()

            if call == Operation.ENCRYPT:
                # Remove SOPS env vars used to specify public keys to force
                # sops to use our config file [1]; so that the file gets
                # encrypted with our keys and not something leaking out of
                # the environment.
                #
                # [1]: https://github.com/getsops/sops/blob/8c567aa8a7cf4802e251e87efc84a1c50b69d4f0/cmd/sops/main.go#L2229
                for var in os.environ:
                    if var.startswith("SOPS_") and var not in {  # allowed:
                        "SOPS_GPG_EXEC",
                        "SOPS_AGE_KEY",
                        "SOPS_AGE_KEY_FILE",
                    }:
                        del environ[var]
                sops_cmd.extend(["encrypt", "--in-place"])
            elif call == Operation.UPDATE_KEYS:
                sops_cmd.extend(["updatekeys", "--yes"])
            elif call != Operation.EDIT:
                known_operations = ",".join(Operation.__members__.values())
                msg = (
                    f"Unsupported sops operation {call.value} "
                    f"(known operations: {known_operations})"
                )
                raise ClanError(msg)
        sops_cmd.append(str(secret_path))

        cmd = nix_shell(["sops", "gnupg", *age_plugins], sops_cmd)
        opts = (
            dataclasses.replace(run_opts, env=environ)
            if run_opts
            else RunOpts(env=environ)
        )
        if call == Operation.EDIT:
            # Use direct stdout / stderr, as else it breaks editor integration.
            # We never need this in our UI. TUI only.
            p1 = subprocess.run(cmd, check=False, text=True)
            return p1.returncode, ""
        p = run(cmd, opts)
        return p.returncode, p.stdout


def get_public_age_keys(contents: str) -> set[str]:
    # we use a set as it's possible we may detect the same key twice, once in a `# comment` and once by recovering it
    # from AGE-SECRET-KEY
    keys: set[str] = set()
    recipient: str | None = None

    for line_number, line in enumerate(contents.splitlines()):
        match = AGE_RECIPIENT_REGEX.match(line)

        if match:
            recipient = match[1]
            if not recipient:
                msg = (
                    f"Empty or invalid recipient on line {line_number}. "
                    "Expected a valid `# recipient: age1...` comment or a recognized recipient format."
                )
                raise ClanError(msg)

            keys.add(recipient)

        if line.startswith("#"):
            continue

        if line.startswith("AGE-PLUGIN-"):
            if not recipient:
                msg = f"Did you forget to precede line {line_number} with it's corresponding `# recipient: age1xxxxxxxx` entry?"
                raise ClanError(msg)

            # reset recipient
            recipient = None

        if line.startswith("AGE-SECRET-KEY-"):
            try:
                keys.add(get_public_age_key_from_private_key(line))
            except Exception as e:
                msg = "Failed to get public key for age private key. Is the key malformed?"
                raise ClanError(msg) from e

            # reset recipient
            recipient = None

    return keys


def get_public_age_key_from_private_key(privkey: str) -> str:
    cmd = nix_shell(["age"], ["age-keygen", "-y"])

    error_msg = "Failed to get public key for age private key. Is the key malformed?"
    res = run(
        cmd,
        RunOpts(input=privkey.encode(), error_msg=error_msg, sensitive_input=True),
    )
    return res.stdout.rstrip(os.linesep).rstrip()


def generate_private_key(out_file: Path | None = None) -> tuple[str, str]:
    cmd = nix_shell(["age"], ["age-keygen"])
    try:
        proc = run(cmd)
        res = proc.stdout.strip()
        pubkey = None
        private_key = None
        for line in res.splitlines():
            if line.startswith("# public key:"):
                pubkey = line.split(":")[1].strip()
            if not line.startswith("#"):
                private_key = line
        if not pubkey:
            msg = "Could not find public key in age-keygen output"
            raise ClanError(msg)
        if not private_key:
            msg = "Could not find private key in age-keygen output"
            raise ClanError(msg)
        if out_file:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.touch(mode=0o600)
            out_file.write_text(res)
    except subprocess.CalledProcessError as e:
        msg = "Failed to generate private sops key"
        raise ClanError(msg) from e
    else:
        return private_key, pubkey


def get_user_name(flake_dir: Path, user: str) -> str:
    """Ask the user for their name until a unique one is provided."""
    while True:
        name = input(
            f"Your key is not yet added to the repository. Enter your user name for which your sops key will be stored in the repository [default: {user}]: ",
        )
        if name:
            user = name
        if not (flake_dir / user).exists():
            return user
        print(f"{flake_dir / user} already exists")


def maybe_get_user(flake_dir: Path, keys: set[SopsKey]) -> set[SopsKey] | None:
    folder = sops_users_folder(flake_dir)

    if folder.exists():
        for user in folder.iterdir():
            if not (user / "key.json").exists():
                continue

            user_keys = read_keys(user)
            if len(keys.intersection(user_keys)):
                return {
                    SopsKey(key.pubkey, user.name, key.key_type, key.source)
                    for key in user_keys
                }

    return None


def default_admin_private_key_path() -> Path:
    raw_path = os.environ.get("SOPS_AGE_KEY_FILE")
    if raw_path:
        return Path(raw_path)
    return user_config_dir() / "sops" / "age" / "keys.txt"


def maybe_get_admin_public_keys() -> list[SopsKey] | None:
    keyring = SopsKey.collect_public_keys()

    if len(keyring) == 0:
        return None

    return keyring


def ensure_admin_public_keys(flake_dir: Path) -> set[SopsKey]:
    keys = maybe_get_admin_public_keys()

    if not keys:
        msg = "No SOPS key found. Please generate one with `clan secrets key generate`."
        raise ClanError(msg)

    user_keys = maybe_get_user(flake_dir, set(keys))

    if not user_keys:
        msg = (
            f"We could not figure out which Clan secrets user you are with the SOPS keys we found:\n"
            f"- {'\n- '.join(f'{key.key_type.name.lower()}: {key.pubkey}' for key in keys)}\n\n"
            f"Please ensure you have created a Clan secrets user and added one of your SOPS keys\n"
            f"to that user.\n"
            f"For more information, see: https://docs.clan.lol/guides/secrets/#add-your-public-keys"
        )
        raise ClanError(msg)

    return user_keys


def update_keys(
    secret_path: Path,
    keys: Iterable[SopsKey],
    age_plugins: list[str] | None = None,
) -> list[Path]:
    secret_path = secret_path / "secret"
    error_msg = f"Could not update keys for {secret_path}"

    rc, _ = sops_run(
        Operation.UPDATE_KEYS,
        secret_path,
        keys,
        run_opts=RunOpts(log=Log.BOTH, error_msg=error_msg),
        age_plugins=age_plugins,
    )
    was_modified = ExitStatus.parse(rc) != ExitStatus.FILE_HAS_NOT_BEEN_MODIFIED
    return [secret_path] if was_modified else []


def encrypt_file(
    secret_path: Path,
    content: str | IO[bytes] | bytes | None,
    pubkeys: list[SopsKey],
    age_plugins: list[str] | None = None,
) -> None:
    folder = secret_path.parent
    folder.mkdir(parents=True, exist_ok=True)

    if not content:
        # This will spawn an editor to edit the file.
        rc, _ = sops_run(
            Operation.EDIT,
            secret_path,
            pubkeys,
            run_opts=RunOpts(),
            age_plugins=age_plugins,
        )
        status = ExitStatus.parse(rc)
        if rc == 0 or status == ExitStatus.FILE_HAS_NOT_BEEN_MODIFIED:
            return
        msg = f"Failed to encrypt {secret_path}: sops exited with {status or rc}"
        raise ClanError(msg)

    # lopter(2024-11-19): imo NamedTemporaryFile does RAII wrong since it
    # creates the file in __init__, when really it should be created in
    # __enter__ (that is in Python __enter__ is actually __init__ from a RAII
    # perspective, and __init__ should just be thought off as syntax sugar to
    # capture extra context), and now the linter is unhappy so hush it. Note
    # that if NamedTemporaryFile created the file in __enter__ then we'd have
    # to change exception handling:
    try:
        source = NamedTemporaryFile(dir="/dev/shm", delete=False)  # noqa: SIM115
    except (FileNotFoundError, PermissionError):
        source = NamedTemporaryFile(delete=False)  # noqa: SIM115
    try:  # swap the secret:
        with source:
            if isinstance(content, str):
                source.file.write(content.encode())
            elif isinstance(content, bytes):
                source.file.write(content)
            elif isinstance(content, io.BufferedReader):
                # lopter@(2024-11-19): mypy is freaking out on the 1st
                #                      argument, idk why, it says:
                #
                # > Cannot infer type argument 1 of "copyfileobj"
                shutil.copyfileobj(content, source.file)  # type: ignore[misc]
            else:
                msg = f"Invalid content type: {type(content)}"
                raise ClanError(msg)
        sops_run(
            Operation.ENCRYPT,
            Path(source.name),
            pubkeys,
            run_opts=RunOpts(log=Log.BOTH),
            age_plugins=age_plugins,
        )
        # atomic copy of the encrypted file
        with NamedTemporaryFile(dir=folder, delete=False) as dest:
            shutil.copyfile(source.name, dest.name)
            Path(dest.name).rename(secret_path)
    finally:
        with suppress(OSError):
            Path(source.name).unlink()


def decrypt_file(secret_path: Path, age_plugins: list[str] | None = None) -> str:
    # decryption uses private keys from the environment or default paths:
    no_public_keys_needed: list[SopsKey] = []

    _, stdout = sops_run(
        Operation.DECRYPT,
        secret_path,
        no_public_keys_needed,
        run_opts=RunOpts(error_msg=f"Could not decrypt {secret_path}"),
        age_plugins=age_plugins,
    )
    return stdout


def get_recipients(secret_path: Path) -> set[SopsKey]:
    sops_attrs = json.loads((secret_path / "secret").read_text())["sops"]
    keys = set()
    for key_type in KeyType:
        recipients = sops_attrs.get(key_type.name.lower())
        if not recipients:
            continue
        for recipient in recipients:
            keys.add(
                SopsKey(
                    pubkey=recipient[key_type.sops_recipient_attr],
                    username="",
                    key_type=key_type,
                    source="sops_file",
                ),
            )
    return keys


def get_meta(secret_path: Path) -> dict:
    meta_path = secret_path.parent / "meta.json"
    if not meta_path.exists():
        return {}
    with meta_path.open() as f:
        return json.load(f)


def write_key(path: Path, key: SopsKey, overwrite: bool) -> None:
    return write_keys(path, [key], overwrite)


def write_keys(path: Path, keys: Iterable[SopsKey], overwrite: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if not overwrite:
            flags |= os.O_EXCL
        fd = os.open(path / "key.json", flags)
    except FileExistsError:
        msg = f"{path.name} already exists in {path}. Use --force to overwrite."
        raise ClanError(msg) from None
    with os.fdopen(fd, "w") as f:
        contents = [
            {"publickey": key.pubkey, "type": key.key_type.name.lower()}
            for key in sorted(keys)
        ]
        json.dump(contents, f, indent=2)


def append_keys(path: Path, keys: Iterable[SopsKey]) -> None:
    path.mkdir(parents=True, exist_ok=True)

    # key file must already exist
    try:
        current_keys = set(read_keys(path))
    except FileNotFoundError:
        msg = f"{path} does not exist."
        raise ClanError(msg) from None

    # add the specified keys to the set
    # de-duplication is natural
    current_keys.update(keys)

    # write the new key set
    return write_keys(path, sorted(current_keys), overwrite=True)


def remove_keys(path: Path, keys: Iterable[SopsKey]) -> None:
    path.mkdir(parents=True, exist_ok=True)

    # key file must already exist
    try:
        current_keys = set(read_keys(path))
    except FileNotFoundError:
        msg = f"{path} does not exist."
        raise ClanError(msg) from None

    current_keys.difference_update(keys)

    if not current_keys:
        msg = f"No keys would remain in {path}. At least one key is required. Aborting."
        raise ClanError(msg)

    # write the new key set
    return write_keys(path, sorted(current_keys), overwrite=True)


def parse_key(key: Any) -> SopsKey:
    if not isinstance(key, dict):
        msg = f"Expected a dict but {type(key)!r} was provided"
        raise ClanError(msg)
    key_type = KeyType.validate(key.get("type"))
    if key_type is None:
        msg = f'Invalid key type in {key}: "{key_type}" (expected one of {", ".join(KeyType.__members__.keys())}).'
        raise ClanError(msg)
    publickey = key.get("publickey")
    if not publickey:
        msg = f"{key} does not contain a public key"
        raise ClanError(msg)
    return SopsKey(publickey, "", key_type, "key_file")


def read_key(path: Path) -> SopsKey:
    keys = read_keys(path)
    if len(keys) != 1:
        msg = f"Expected exactly one key but {len(keys)} were found"
        raise ClanError(msg)
    return next(iter(keys))


def read_keys(path: Path) -> set[SopsKey]:
    with Path(path / "key.json").open() as f:
        try:
            keys = json.load(f)
        except json.JSONDecodeError as e:
            msg = f"Failed to decode {path.name}: {e}"
            raise ClanError(msg) from e

    if isinstance(keys, dict):
        return {parse_key(keys)}
    if isinstance(keys, list):
        return set(map(parse_key, keys))
    msg = f"Expected a dict or array but {type(keys)!r} was provided"
    raise ClanError(msg)
