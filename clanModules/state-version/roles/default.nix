{ config, lib, ... }:
let
  var = config.clan.core.vars.generators.state-version.files.version or { };
in
{

  warnings = [
    ''
      The clan.state-version service is deprecated and will be
      removed on 2025-07-15 in favor of a nix option.

      Please migrate your configuration to use `clan.core.settings.state-version.enable = true` instead.
    ''
  ];

  system.stateVersion = lib.mkDefault (lib.removeSuffix "\n" var.value);

  clan.core.vars.generators.state-version = {
    files.version = {
      secret = false;
      value = lib.mkDefault config.system.nixos.release;
    };
    runtimeInputs = [ ];
    script = ''
      echo -n ${config.system.stateVersion} > "$out"/version
    '';
  };
}
