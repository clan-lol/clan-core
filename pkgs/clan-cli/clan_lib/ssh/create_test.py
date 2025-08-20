from pathlib import Path

from clan_lib.ssh.create import create_secret_key_nixos_anywhere


def test_clan_generate_sshkeys(temporary_home: Path) -> None:  # noqa: ARG001
    keypair = create_secret_key_nixos_anywhere()

    assert keypair.private.exists()
    assert keypair.public.exists()
    assert keypair.private.is_file()
    assert keypair.public.is_file()
    assert (
        keypair.private.parent
        == Path("~/.config/clan/nixos-anywhere/keys").expanduser()
    )
    assert (
        keypair.public.parent == Path("~/.config/clan/nixos-anywhere/keys").expanduser()
    )
    assert keypair.private.name == "id_ed25519"
    assert keypair.public.name == "id_ed25519.pub"
    assert "PRIVATE KEY" in keypair.private.read_text()
    assert "ssh-ed25519" in keypair.public.read_text()

    new_keypair = create_secret_key_nixos_anywhere()

    assert new_keypair.private == keypair.private
    assert new_keypair.public == keypair.public
