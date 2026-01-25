import argparse
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from clan_cli.tests.age_keys import KeyPair
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.tests.test_vars import invalidate_flake_cache
from clan_cli.vars.check import check_vars
from clan_cli.vars.generate import generate_command
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.vars._types import GeneratorId, PerMachine, Shared
from clan_lib.vars.generator import Generator
from clan_lib.vars.list import stringify_all_vars
from clan_lib.vars.secret_modules import age
from clan_lib.vars.var import Var

# ── Helpers ──────────────────────────────────────────────────────────────


def setup_age_flake(
    flake: ClanFlake,
    monkeypatch: pytest.MonkeyPatch,
    age_key: KeyPair,
    machines: list[str] | None = None,
) -> tuple[Flake, Path]:
    """Set up a flake with age backend and return (Flake, age_key_file_path).

    Creates clan.nix with recipients, writes the age key file,
    sets AGE_KEYFILE, and commits.
    """
    if machines is None:
        machines = ["my_machine"]

    # Set up machine configs
    for m in machines:
        config = flake.machines[m] = create_test_machine_config()
        config["clan"]["core"]["vars"]["settings"]["secretStore"] = "age"

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Write clan.nix with recipients for all machines
    hosts_block = "\n".join(
        f'  vars.settings.recipients.hosts.{m} = ["{age_key.pubkey}"];'
        for m in machines
    )
    (flake.path / "clan.nix").write_text(f"{{\n{hosts_block}\n}}\n")

    # Set up age key file
    age_key_dir = flake.path / ".age"
    age_key_dir.mkdir()
    age_key_file = age_key_dir / "key.txt"
    age_key_file.write_text(age_key.privkey)
    monkeypatch.setenv("AGE_KEYFILE", str(age_key_file))

    # Commit
    subprocess.run(["git", "add", "."], cwd=flake.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "setup age backend"],
        cwd=flake.path,
        check=True,
    )

    return Flake(str(flake.path)), age_key_file


def make_generator(
    name: str,
    placement: PerMachine | Shared,
    flake: Flake,
    files: list[Var] | None = None,
) -> Generator:
    """Create a Generator object for testing store methods."""
    return Generator(
        key=GeneratorId(name=name, placement=placement),
        files=files or [],
        _flake=flake,
    )


def make_var(
    name: str,
    machines: list[str],
    secret: bool = True,
    deploy: bool = True,
    needed_for: str = "services",
    owner: str = "root",
    group: str = "root",
    mode: int = 0o400,
) -> Var:
    """Create a Var object for testing."""
    return Var(
        id=f"test/{name}",
        name=name,
        machines=machines,
        secret=secret,
        deploy=deploy,
        needed_for=needed_for,
        owner=owner,
        group=group,
        mode=mode,
    )


# ── Existing tests ──────────────────────────────────────────────────────


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_var_age(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test the age secret store backend."""
    age_key = age_keys[0]

    # Set up machine configuration with age backend
    config = flake.machines["my_machine"] = create_test_machine_config()
    clan_vars = config["clan"]["core"]["vars"]
    clan_vars["settings"]["secretStore"] = "age"

    # Create generators with secrets
    my_generator = clan_vars["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = 'echo hello > "$out"/my_secret'

    my_generator2 = clan_vars["generators"]["my_generator2"]
    my_generator2["files"]["my_secret2"]["secret"] = True
    my_generator2["script"] = 'echo world > "$out"/my_secret2'

    my_shared_generator = clan_vars["generators"]["my_shared_generator"]
    my_shared_generator["share"] = True
    my_shared_generator["files"]["my_shared_secret"]["secret"] = True
    my_shared_generator["script"] = 'echo shared > "$out"/my_shared_secret'

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Write clan.nix with age recipients configuration
    clan_nix_content = f"""
{{
  vars.settings.recipients.hosts.my_machine = [
    "{age_key.pubkey}"
  ];
}}
"""
    (flake.path / "clan.nix").write_text(clan_nix_content)

    # Set up age key file
    age_key_dir = flake.path / ".age"
    age_key_dir.mkdir()
    age_key_file = age_key_dir / "key.txt"
    age_key_file.write_text(age_key.privkey)

    # Set AGE_KEYFILE environment variable
    monkeypatch.setenv("AGE_KEYFILE", str(age_key_file))

    # Commit the changes
    subprocess.run(["git", "add", "."], cwd=flake.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add clan.nix with age recipients"],
        cwd=flake.path,
        check=True,
    )

    flake_obj = Flake(str(flake.path))
    machine = Machine(name="my_machine", flake=flake_obj)

    # Generate secrets
    assert not check_vars(machine.name, machine.flake)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    assert check_vars(machine.name, machine.flake)

    # Verify the age store works
    store = age.SecretStore(flake=flake_obj)

    my_generator_obj = make_generator(
        "my_generator", PerMachine("my_machine"), flake_obj
    )
    my_generator_shared = make_generator("my_generator", Shared(), flake_obj)
    my_shared_generator_obj = make_generator("my_shared_generator", Shared(), flake_obj)
    my_shared_generator_not_shared = make_generator(
        "my_shared_generator", PerMachine("my_machine"), flake_obj
    )

    # Check secrets exist in the right locations
    assert store.exists(my_generator_obj.key, "my_secret")
    assert not store.exists(my_generator_shared.key, "my_secret")
    assert store.exists(my_shared_generator_obj.key, "my_shared_secret")
    assert not store.exists(my_shared_generator_not_shared.key, "my_shared_secret")

    # Check secret content
    assert store.get(my_generator_obj.key, "my_secret").decode() == "hello\n"
    assert (
        store.get(my_shared_generator_obj.key, "my_shared_secret").decode()
        == "shared\n"
    )

    # Check that secrets are in the stringified output
    vars_text = stringify_all_vars(machine)
    assert "my_generator/my_secret" in vars_text

    # Test deletion
    store.delete(my_generator_obj.key, "my_secret")
    assert not store.exists(my_generator_obj.key, "my_secret")

    # Test delete_store
    store.delete_store("my_machine")
    store.delete_store("my_machine")  # Check idempotency

    my_generator2_obj = make_generator(
        "my_generator2", PerMachine("my_machine"), flake_obj
    )
    assert not store.exists(my_generator2_obj.key, "my_secret2")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_var_age_minimal_select_calls(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test that age backend doesn't make unnecessary select calls."""
    age_key = age_keys[0]

    config = flake.machines["my_machine"] = create_test_machine_config()
    clan_vars = config["clan"]["core"]["vars"]
    clan_vars["settings"]["secretStore"] = "age"

    # Create a simple generator with a secret
    my_generator = clan_vars["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = 'echo hello > "$out"/my_secret'

    # Add machine2 and machine3 with the same configuration
    flake.machines["machine2"] = config.copy()
    flake.machines["machine3"] = config.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Write clan.nix with age recipients configuration for all machines
    clan_nix_content = f"""
{{
  vars.settings.recipients.hosts.my_machine = [
    "{age_key.pubkey}"
  ];
  vars.settings.recipients.hosts.machine2 = [
    "{age_key.pubkey}"
  ];
  vars.settings.recipients.hosts.machine3 = [
    "{age_key.pubkey}"
  ];
}}
"""
    (flake.path / "clan.nix").write_text(clan_nix_content)

    # Set up age key file
    age_key_dir = flake.path / ".age"
    age_key_dir.mkdir()
    age_key_file = age_key_dir / "key.txt"
    age_key_file.write_text(age_key.privkey)

    # Set AGE_KEYFILE environment variable
    monkeypatch.setenv("AGE_KEYFILE", str(age_key_file))

    # Commit the changes
    subprocess.run(["git", "add", "."], cwd=flake.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add clan.nix with age recipients"],
        cwd=flake.path,
        check=True,
    )

    # Create a fresh flake object and invalidate cache to ensure clean state
    invalidate_flake_cache(flake.path)
    flake_obj = Flake(str(flake.path))

    # Generate the secrets
    generate_command(
        argparse.Namespace(
            machines=["my_machine", "machine2", "machine3"],
            generator=None,
            flake=flake_obj,
            regenerate=False,
            no_sandbox=False,
        )
    )

    # The optimization should result in minimal cache misses.
    # We expect exactly 3 cache misses:
    # 1. Inventory selectors (from list_full_machines)
    # 2. Generator metadata selectors (from generate_command precache)
    # 3. finalScript and store selectors (from run_generators precache)

    # Print stack traces if we have more cache misses than expected
    if flake_obj._cache_misses > 3:
        flake_obj.print_cache_miss_analysis(title="Cache miss analysis for age backend")

    assert flake_obj._cache_misses == 3, (
        f"Expected exactly 3 cache misses for age backend, "
        f"got {flake_obj._cache_misses}."
    )

    # Verify the secret was actually generated
    store = age.SecretStore(flake=flake_obj)
    generator = make_generator("my_generator", PerMachine("my_machine"), flake_obj)
    assert store.exists(generator.key, "my_secret")
    assert store.get(generator.key, "my_secret").decode() == "hello\n"


# ── New tests ────────────────────────────────────────────────────────────


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_get_identity_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test get_identity with AGE_KEY and AGE_KEYFILE env vars."""
    flake_obj, age_key_file = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    # AGE_KEYFILE is already set by setup_age_flake
    content, path = store.get_identity()
    assert content is None
    assert path == age_key_file

    # Test AGE_KEY takes priority
    monkeypatch.setenv("AGE_KEY", age_keys[0].privkey)
    content, path = store.get_identity()
    assert content == age_keys[0].privkey
    assert path is None

    # Test AGE_KEYFILE with non-existent path
    monkeypatch.delenv("AGE_KEY")
    monkeypatch.setenv("AGE_KEYFILE", "/nonexistent/path")
    with pytest.raises(ClanError, match="non-existent file"):
        store.get_identity()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_get_identity_fallback_paths(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
    tmp_path: Path,
) -> None:
    """Test get_identity falls back to well-known paths."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    # Clear env vars
    monkeypatch.delenv("AGE_KEY", raising=False)
    monkeypatch.delenv("AGE_KEYFILE", raising=False)

    # Patch the search paths to use tmp_path
    fake_identity = tmp_path / "age" / "identities"
    fake_identity.parent.mkdir(parents=True)
    fake_identity.write_text(age_keys[0].privkey)

    monkeypatch.setattr(
        age.SecretStore,
        "_IDENTITY_SEARCH_PATHS",
        [fake_identity],
    )

    content, path = store.get_identity()
    assert content is None
    assert path == fake_identity


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_get_identity_none_found(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test get_identity raises when no identity is available."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    monkeypatch.delenv("AGE_KEY", raising=False)
    monkeypatch.delenv("AGE_KEYFILE", raising=False)
    monkeypatch.setattr(
        age.SecretStore,
        "_IDENTITY_SEARCH_PATHS",
        [Path("/nonexistent/1"), Path("/nonexistent/2")],
    )

    with pytest.raises(ClanError, match="No age identity found"):
        store.get_identity()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_health_check(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test health_check detects missing recipients, identity, and passes when ok."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    # Should pass — recipients configured, identity available, no machine key yet is ok
    result = store.health_check("my_machine", [])
    assert result is None, f"Expected None, got: {result}"

    # Missing recipients
    (flake_obj.path / "clan.nix").write_text("{}\n")
    subprocess.run(["git", "add", "."], cwd=flake_obj.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "remove recipients"],
        cwd=flake_obj.path,
        check=True,
    )
    invalidate_flake_cache(Path(flake_obj.path))
    store2 = age.SecretStore(flake=Flake(str(flake_obj.path)))
    result = store2.health_check("my_machine", [])
    assert result is not None
    assert "recipients" in result.lower()

    # Missing identity
    monkeypatch.delenv("AGE_KEYFILE")
    monkeypatch.delenv("AGE_KEY", raising=False)
    monkeypatch.setattr(
        age.SecretStore,
        "_IDENTITY_SEARCH_PATHS",
        [Path("/nonexistent")],
    )
    result = store.health_check("my_machine", [])
    assert result is not None
    assert "identity" in result.lower()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_ensure_machine_key(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test ensure_machine_key creates keypair and encrypts privkey to user."""
    age_key = age_keys[0]
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_key)
    store = age.SecretStore(flake=flake_obj)

    # No key yet
    assert not store.machine_pubkey_file("my_machine").exists()
    assert not store.machine_encrypted_key_file("my_machine").exists()

    # Generate
    store.ensure_machine_key("my_machine")

    # Pubkey exists and is valid
    pubkey = store.get_machine_pubkey("my_machine")
    assert pubkey.startswith("age1")

    # Encrypted key exists
    assert store.machine_encrypted_key_file("my_machine").exists()

    # Can decrypt machine key with user identity
    machine_privkey = store.decrypt_machine_key("my_machine")
    assert b"AGE-SECRET-KEY-" in machine_privkey

    # Idempotent — calling again doesn't change anything
    pubkey_before = pubkey
    store.ensure_machine_key("my_machine")
    assert store.get_machine_pubkey("my_machine") == pubkey_before


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_rekey_machine_key(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test rekey_machine_key re-encrypts the machine key to new recipients."""
    age_key = age_keys[0]
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_key)
    store = age.SecretStore(flake=flake_obj)

    store.ensure_machine_key("my_machine")
    original_privkey = store.decrypt_machine_key("my_machine")
    original_encrypted = store.machine_encrypted_key_file("my_machine").read_bytes()

    # Re-key (same recipients, but ciphertext should change due to age randomness)
    store.rekey_machine_key("my_machine")

    # Private key content should be the same
    rekeyed_privkey = store.decrypt_machine_key("my_machine")
    assert rekeyed_privkey == original_privkey

    # Ciphertext should differ (age uses random nonces)
    rekeyed_encrypted = store.machine_encrypted_key_file("my_machine").read_bytes()
    assert rekeyed_encrypted != original_encrypted


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_set_and_get_per_machine(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test _set and get for per-machine secrets."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    var = make_var("my_secret", machines=["my_machine"])
    gen = make_generator(
        "my_gen",
        PerMachine("my_machine"),
        flake_obj,
        files=[var],
    )

    # Set a secret
    result_path = store._set(gen, var, b"secret-value")
    assert result_path is not None
    assert result_path.exists()

    # Get it back
    value = store.get(gen.key, "my_secret")
    assert value == b"secret-value"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_set_and_get_shared(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test _set and get for shared secrets with multiple machines."""
    flake_obj, _ = setup_age_flake(
        flake, monkeypatch, age_keys[0], machines=["machine_a", "machine_b"]
    )
    store = age.SecretStore(flake=flake_obj)

    var = make_var("shared_secret", machines=["machine_a", "machine_b"])
    gen = make_generator(
        "shared_gen",
        Shared(),
        flake_obj,
        files=[var],
    )

    # Set — should encrypt to both machines' pubkeys
    store._set(gen, var, b"shared-value")

    # Both machines should be able to decrypt
    value = store.get(gen.key, "shared_secret")
    assert value == b"shared-value"

    # Verify both machine keys were created
    assert store.machine_pubkey_file("machine_a").exists()
    assert store.machine_pubkey_file("machine_b").exists()

    # Decrypt using each machine's key individually to verify multi-recipient
    for machine_name in ["machine_a", "machine_b"]:
        machine_key = store.decrypt_machine_key(machine_name)
        secret_file = store.secret_path(gen.key, "shared_secret")
        plaintext = store._run_age_decrypt_with_key(secret_file, machine_key)
        assert plaintext == b"shared-value"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_get_shared_finds_any_machine_key(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test that get() for Shared secrets finds any available machine key."""
    flake_obj, _ = setup_age_flake(
        flake, monkeypatch, age_keys[0], machines=["machine_a", "machine_b"]
    )
    store = age.SecretStore(flake=flake_obj)

    var = make_var("shared_secret", machines=["machine_a", "machine_b"])
    gen = make_generator("shared_gen", Shared(), flake_obj, files=[var])

    store._set(gen, var, b"shared-value")

    # get() with Shared placement should find any machine key to decrypt
    value = store.get(gen.key, "shared_secret")
    assert value == b"shared-value"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_populate_dir(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test populate_dir creates correct upload directory structure."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    # Create vars for different phases
    service_var = make_var("svc_secret", machines=["my_machine"], needed_for="services")
    user_var = make_var("usr_secret", machines=["my_machine"], needed_for="users")
    activation_var = make_var(
        "act_secret", machines=["my_machine"], needed_for="activation"
    )
    perm_var = make_var(
        "perm_secret",
        machines=["my_machine"],
        needed_for="services",
        owner="nobody",
        group="nogroup",
        mode=0o440,
    )

    gen_svc = make_generator(
        "gen_svc", PerMachine("my_machine"), flake_obj, files=[service_var]
    )
    gen_usr = make_generator(
        "gen_usr", PerMachine("my_machine"), flake_obj, files=[user_var]
    )
    gen_act = make_generator(
        "gen_act", PerMachine("my_machine"), flake_obj, files=[activation_var]
    )
    gen_perm = make_generator(
        "gen_perm", PerMachine("my_machine"), flake_obj, files=[perm_var]
    )

    # Set secrets
    store._set(gen_svc, service_var, b"service-secret")
    store._set(gen_usr, user_var, b"user-secret")
    store._set(gen_act, activation_var, b"activation-secret")
    store._set(gen_perm, perm_var, b"perm-secret")

    # Populate upload directory
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        store.populate_dir(
            [gen_svc, gen_usr, gen_act, gen_perm],
            "my_machine",
            output_dir,
            phases=["services", "users", "activation"],
        )

        # key.txt exists and contains a valid age secret key
        key_file = output_dir / "key.txt"
        assert key_file.exists()
        key_content = key_file.read_text()
        assert "AGE-SECRET-KEY-" in key_content

        # Service/user secrets are delivered via the nix store,
        # but activation secrets are uploaded as plaintext
        assert not (output_dir / "secrets").exists()
        assert not (output_dir / "user-secrets").exists()
        assert not (output_dir / "manifest.json").exists()

        # Activation secrets are decrypted and uploaded as plaintext
        act_file = output_dir / "activation" / "gen_act" / "act_secret"
        assert act_file.exists()
        assert act_file.read_bytes() == b"activation-secret"

        # Can decrypt a secret from the repo with the machine key
        svc_secret_file = store.secret_path(gen_svc.key, "svc_secret")
        result = subprocess.run(
            ["age", "--decrypt", "-i", str(key_file)],
            input=svc_secret_file.read_bytes(),
            capture_output=True,
            check=True,
        )
        assert result.stdout == b"service-secret"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_fix_shared_reencrypt(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test fix() re-encrypts shared secrets when machines change."""
    flake_obj, _ = setup_age_flake(
        flake, monkeypatch, age_keys[0], machines=["machine_a", "machine_b"]
    )
    store = age.SecretStore(flake=flake_obj)

    # Create a shared secret encrypted only to machine_a
    var = make_var("shared_secret", machines=["machine_a"])
    gen_a_only = make_generator("shared_gen", Shared(), flake_obj, files=[var])
    store._set(gen_a_only, var, b"shared-value")

    # machine_b can't decrypt it yet
    store.ensure_machine_key("machine_b")
    machine_b_key = store.decrypt_machine_key("machine_b")
    secret_file = store.secret_path(gen_a_only.key, "shared_secret")
    with pytest.raises(ClanError, match="Failed to decrypt"):
        store._run_age_decrypt_with_key(secret_file, machine_b_key)

    # Now fix with a generator that includes both machines
    var_both = make_var("shared_secret", machines=["machine_a", "machine_b"])
    gen_both = make_generator("shared_gen", Shared(), flake_obj, files=[var_both])
    store.fix("machine_b", [gen_both])

    # Now machine_b can decrypt
    plaintext = store._run_age_decrypt_with_key(secret_file, machine_b_key)
    assert plaintext == b"shared-value"

    # machine_a can still decrypt
    machine_a_key = store.decrypt_machine_key("machine_a")
    plaintext = store._run_age_decrypt_with_key(secret_file, machine_a_key)
    assert plaintext == b"shared-value"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_incremental_generate_shared_secret(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Generating machines one at a time must not lock others out of shared secrets.

    Scenario: machines A and B share a generator. Running
    `clan vars generate A` then `clan vars generate B` must leave both
    machines able to decrypt the shared secret.  The fix() workaround in
    run_generators re-encrypts shared secrets to all machines known to
    the clan, not just the ones passed on the command line.
    """
    age_key = age_keys[0]

    # Set up both machines with a shared generator
    for m in ["machine_a", "machine_b"]:
        config = flake.machines[m] = create_test_machine_config()
        clan_vars = config["clan"]["core"]["vars"]
        clan_vars["settings"]["secretStore"] = "age"
        shared_gen = clan_vars["generators"]["cluster_token"]
        shared_gen["share"] = True
        shared_gen["files"]["token"]["secret"] = True
        shared_gen["script"] = 'echo cluster-secret > "$out"/token'

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Write clan.nix with recipients for both machines
    (flake.path / "clan.nix").write_text(
        f"{{\n"
        f'  vars.settings.recipients.hosts.machine_a = ["{age_key.pubkey}"];\n'
        f'  vars.settings.recipients.hosts.machine_b = ["{age_key.pubkey}"];\n'
        f"}}\n"
    )

    # Set up age key
    age_key_dir = flake.path / ".age"
    age_key_dir.mkdir()
    age_key_file = age_key_dir / "key.txt"
    age_key_file.write_text(age_key.privkey)
    monkeypatch.setenv("AGE_KEYFILE", str(age_key_file))

    subprocess.run(["git", "add", "."], cwd=flake.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "setup"],
        cwd=flake.path,
        check=True,
    )

    # Step 1: Generate only machine_a
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine_a"])

    store = age.SecretStore(flake=Flake(str(flake.path)))
    gen_id = GeneratorId(name="cluster_token", placement=Shared())

    # Shared secret exists and machine_a can decrypt
    assert store.exists(gen_id, "token")
    key_a = store.decrypt_machine_key("machine_a")
    secret_file = store.secret_path(gen_id, "token")
    assert store._run_age_decrypt_with_key(secret_file, key_a) == b"cluster-secret\n"

    # Step 2: Generate only machine_b
    invalidate_flake_cache(flake.path)
    cli.run(
        ["vars", "generate", "--regenerate", "--flake", str(flake.path), "machine_b"]
    )

    # Recreate store after cache invalidation
    store = age.SecretStore(flake=Flake(str(flake.path)))

    # Both machines must be able to decrypt the shared secret
    key_a = store.decrypt_machine_key("machine_a")
    key_b = store.decrypt_machine_key("machine_b")
    secret_file = store.secret_path(gen_id, "token")

    assert store._run_age_decrypt_with_key(secret_file, key_a) == b"cluster-secret\n", (
        "machine_a lost access to shared secret after generating machine_b"
    )
    assert store._run_age_decrypt_with_key(secret_file, key_b) == b"cluster-secret\n", (
        "machine_b cannot decrypt shared secret after incremental generate"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_error_get_nonexistent(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test get() raises for non-existent secrets."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    gen_id = GeneratorId(name="nonexistent", placement=PerMachine("my_machine"))
    with pytest.raises(ClanError, match="Secret file not found"):
        store.get(gen_id, "missing_secret")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_error_get_no_machine_key(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test get() raises when no machine key can decrypt."""
    flake_obj, _ = setup_age_flake(
        flake, monkeypatch, age_keys[0], machines=["machine_a"]
    )
    store = age.SecretStore(flake=flake_obj)

    # Create a shared secret (so it's stored at the shared path)
    var = make_var("my_secret", machines=["machine_a"])
    gen = make_generator("my_gen", Shared(), flake_obj, files=[var])
    store._set(gen, var, b"secret-value")

    # Remove the machine key dir so get() can't find any key to decrypt with
    shutil.rmtree(store.machine_key_dir("machine_a"))

    gen_shared = GeneratorId(name="my_gen", placement=Shared())
    with pytest.raises(ClanError, match="no accessible machine key"):
        store.get(gen_shared, "my_secret")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_error_missing_machine_pubkey(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test get_machine_pubkey raises for non-existent machine."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    with pytest.raises(ClanError, match="No machine key found"):
        store.get_machine_pubkey("nonexistent_machine")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_delete_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Test delete removes files and cleans up empty directories."""
    flake_obj, _ = setup_age_flake(flake, monkeypatch, age_keys[0])
    store = age.SecretStore(flake=flake_obj)

    var = make_var("my_secret", machines=["my_machine"])
    gen = make_generator("my_gen", PerMachine("my_machine"), flake_obj, files=[var])
    store._set(gen, var, b"secret-value")

    secret_file = store.secret_path(gen.key, "my_secret")
    assert secret_file.exists()
    parent_dir = secret_file.parent

    store.delete(gen.key, "my_secret")
    assert not secret_file.exists()
    # Parent directories should be cleaned up
    assert not parent_dir.exists()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_age_delete_store_leaves_shared_secrets_untouched(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list[KeyPair],
) -> None:
    """Deleting a machine's store must not modify shared secrets.

    Shared secrets are left as-is when a machine is removed.  Remaining
    machines can still decrypt with their own keys.  Cleanup of stale
    shared secrets is deferred to an explicit prune command.
    """
    flake_obj, _ = setup_age_flake(
        flake, monkeypatch, age_keys[0], machines=["machine_a", "machine_b"]
    )
    store = age.SecretStore(flake=flake_obj)

    # Create a shared secret encrypted to both machines
    var = make_var("shared_secret", machines=["machine_a", "machine_b"])
    gen = make_generator("shared_gen", Shared(), flake_obj, files=[var])
    store._set(gen, var, b"shared-value")

    secret_file = store.secret_path(gen.key, "shared_secret")
    ciphertext_before = secret_file.read_bytes()

    # Delete machine_b's store (per-machine secrets + keys)
    store.delete_store("machine_b")

    # Shared secret file is unchanged (same ciphertext)
    assert secret_file.exists()
    assert secret_file.read_bytes() == ciphertext_before

    # machine_a can still decrypt the shared secret
    key_a = store.decrypt_machine_key("machine_a")
    assert store._run_age_decrypt_with_key(secret_file, key_a) == b"shared-value"
