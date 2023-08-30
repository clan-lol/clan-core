{ ... } @ core: {
  flake.flakeModules.clan-config = { self, inputs, ... }:
    let

      # take the default nixos configuration
      options = self.nixosConfigurations.default.options;

      # this is actually system independent as it uses toFile
      docs = inputs.nixpkgs.legacyPackages.x86_64-linux.nixosOptionsDoc {
        inherit options;
      };

      optionsJSONFile = docs.optionsJSON.options;

      warnIfNoDefaultConfig = return:
        if ! self ? nixosConfigurations.default
        then
          builtins.trace
            "WARNING: .#nixosConfigurations.default could not be found. Please define it."
            return
        else return;

    in
    {
      flake.clanOptions = warnIfNoDefaultConfig optionsJSONFile;

      flake.clanSettings = self + /clan-settings.json;

      perSystem = { pkgs, ... }: {
        devShells.clan-config = pkgs.mkShell {
          packages = [
            core.config.flake.packages.${pkgs.system}.clan-cli
          ];
          shellHook = ''
            export CLAN_OPTIONS_FILE=$(nix eval --raw .#clanOptions)
            export XDG_DATA_DIRS="${core.config.flake.packages.${pkgs.system}.clan-cli}/share''${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
            export fish_complete_path="${core.config.flake.packages.${pkgs.system}.clan-cli}/share/fish/vendor_completions.d''${fish_complete_path:+:$fish_complete_path}"
          '';
        };
      };
    };
}
