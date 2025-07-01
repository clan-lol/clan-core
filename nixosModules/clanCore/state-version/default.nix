{
  lib,
  config,
  ...
}:
let
  var = config.clan.core.vars.generators.state-version.files.version or { };
in
{
  options.clan.core.settings.state-version = {
    enable = lib.mkEnableOption "automatic state-version generation.

    The option will take the specified version, if one is already supplied through
    the config or generate one if not";
  };

  config = lib.mkIf (config.clan.core.settings.state-version.enable) {
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
  };
}
