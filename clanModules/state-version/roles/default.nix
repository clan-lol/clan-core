{ config, lib, ... }:
let
  var = config.clan.core.vars.generators.state-version.files.version or { };
in
{

  warnings = [
    "The clan.state-version module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
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
