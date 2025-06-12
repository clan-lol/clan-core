{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/state-version";
  manifest.description = "Automatically generate the state version of the nixos installation.";
  manifest.categories = [ "System" ];

  roles.default = {

    perInstance =
      { ... }:
      {
        nixosModule =
          {
            config,
            lib,
            ...
          }:
          let
            var = config.clan.core.vars.generators.state-version.files.version or { };
          in
          {
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
      };
  };

}
