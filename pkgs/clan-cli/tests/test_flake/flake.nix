{
  # this placeholder is replaced by the path to nixpkgs
  inputs.nixpkgs.url = "__NIXPKGS__";

  outputs =
    inputs':
    let
      # fake clan-core input
      fake-clan-core = {
        clanModules.fake-module = ./fake-module.nix;
      };
      inputs = inputs' // {
        clan-core = fake-clan-core;
      };
      machineSettings = (
        if builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE" != "" then
          builtins.fromJSON (builtins.readFile (builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE"))
        else if builtins.pathExists ./machines/machine1/settings.json then
          builtins.fromJSON (builtins.readFile ./machines/machine1/settings.json)
        else
          { }
      );
      machineImports = map (module: fake-clan-core.clanModules.${module}) (
        machineSettings.clanImports or [ ]
      );
    in
    {
      nixosConfigurations.machine1 = inputs.nixpkgs.lib.nixosSystem {
        modules = machineImports ++ [
          ./nixosModules/machine1.nix
          machineSettings
          (
            {
              lib,
              options,
              pkgs,
              ...
            }:
            {
              config = {
                nixpkgs.hostPlatform = "x86_64-linux";
                # speed up by not instantiating nixpkgs twice and disable documentation
                nixpkgs.pkgs = inputs.nixpkgs.legacyPackages.x86_64-linux;
                documentation.enable = false;
              };
              options.clan.core.optionsNix = lib.mkOption {
                type = lib.types.raw;
                internal = true;
                readOnly = true;
                default = (pkgs.nixosOptionsDoc { inherit options; }).optionsNix;
                defaultText = "optionsNix";
                description = ''
                  This is to export nixos options used for `clan config`
                '';
              };
              options.clanImports = lib.mkOption {
                type = lib.types.listOf lib.types.str;
                description = ''
                  A list of imported module names imported from clan-core.clanModules.<name>
                  The buildClan function will automatically import these modules for the current machine.
                '';
              };
            }
          )
        ];
      };
    };
}
