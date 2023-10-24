{
  # this placeholder is replaced by the path to nixpkgs
  inputs.nixpkgs.url = "__NIXPKGS__";

  outputs = inputs: {
    nixosConfigurations.machine1 = inputs.nixpkgs.lib.nixosSystem {
      modules = [
        ./nixosModules/machine1.nix
        (
          if builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE" != ""
          then builtins.fromJSON (builtins.readFile (builtins.getEnv "CLAN_MACHINE_SETTINGS_FILE"))
          else if builtins.pathExists ./machines/machine1/settings.json
          then builtins.fromJSON (builtins.readFile ./machines/machine1/settings.json)
          else { }
        )
        ({ lib, options, pkgs, ... }: {
          config = {
            nixpkgs.hostPlatform = "x86_64-linux";
            # speed up by not instantiating nixpkgs twice and disable documentation
            nixpkgs.pkgs = inputs.nixpkgs.legacyPackages.x86_64-linux;
            documentation.enable = false;
          };
          options.clanCore.optionsNix = lib.mkOption {
            type = lib.types.raw;
            internal = true;
            readOnly = true;
            default = (pkgs.nixosOptionsDoc { inherit options; }).optionsNix;
            defaultText = "optionsNix";
            description = ''
              This is to export nixos options used for `clan config`
            '';
          };
        })
      ];
    };
  };
}
