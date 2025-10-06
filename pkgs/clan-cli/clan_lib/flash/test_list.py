import logging
import os
from pathlib import Path

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config

from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.flake import ClanSelectError, Flake
from clan_lib.flash.flash import SystemConfig, build_system_config_nix
from clan_lib.flash.list import list_keymaps, list_languages
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config

log = logging.getLogger(__name__)


@pytest.mark.with_core
def test_language_list() -> None:
    languages = list_languages()
    assert isinstance(languages, list)
    assert "en_US.UTF-8" in languages  # Common locale
    assert "fr_FR.UTF-8" in languages  # Common locale
    assert "de_DE.UTF-8" in languages  # Common locale


@pytest.mark.with_core
def test_flash_config(flake: ClanFlake, test_root: Path) -> None:
    languages = list_languages()
    keymaps = list_keymaps()

    host_key = test_root / "data" / "ssh_host_ed25519_key"

    test_langs = list(
        filter(
            lambda x: "zh_CN" in x,
            languages,
        )
    )

    for test_lang in test_langs:
        log.info(f"Testing language: {test_lang}")
        sys_config = SystemConfig(
            language=test_lang,
            keymap=keymaps[3],
            ssh_keys_path=[str(host_key)],
        )

        result = build_system_config_nix(sys_config)

        config = flake.machines["my_machine"] = create_test_machine_config(
            nix_config()["system"]
        )
        config["boot"]["loader"]["grub"]["devices"] = ["/dev/vda"]
        config["fileSystems"]["/"]["device"] = "/dev/vda"
        config.update(result)
        flake.refresh()

        # In the sandbox, building fails due to network restrictions (can't download dependencies)
        # Outside the sandbox, the build should succeed
        in_sandbox = os.environ.get("IN_NIX_SANDBOX") == "1"

        machine = Machine(name="my_machine", flake=Flake(str(flake.path)))
        if in_sandbox:
            # In sandbox: expect build to fail due to network restrictions
            with pytest.raises(ClanSelectError) as select_error:
                Path(machine.select("config.system.build.toplevel"))
            # The error should be a select_error without a failed_attr
            cmd_error = select_error.value.__cause__
            assert cmd_error is not None
            assert isinstance(cmd_error, ClanCmdError)
            assert "nixos-system-my_machine" in str(cmd_error.cmd.stderr)
        else:
            try:
                # Outside sandbox: build should succeed
                toplevel_path = Path(machine.select("config.system.build.toplevel"))
                assert toplevel_path.exists()
            except ClanSelectError as e:
                if "Error: unsupported locales detected" in str(e.__cause__):
                    msg = f"Locale '{sys_config.language}' is not supported on this system."
                    raise ClanError(msg) from e
                raise
            # Verify it's a NixOS system by checking for expected content
            assert "nixos-system-my_machine" in str(toplevel_path)


@pytest.mark.with_core
def test_list_keymaps() -> None:
    keymaps = list_keymaps()
    assert isinstance(keymaps, list)
    assert "us" in keymaps  # Common keymap
    assert "uk" in keymaps  # Common keymap
    assert "de" in keymaps  # Common keymap
