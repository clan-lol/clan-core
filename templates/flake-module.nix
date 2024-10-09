{ self, inputs, ... }:
{
  flake = (import ./flake.nix).outputs { } // {
    checks.x86_64-linux.template-minimal =
      let
        path = self.templates.minimal.path;
        initialized = inputs.nixpkgs.legacyPackages.x86_64-linux.runCommand "minimal-clan-flake" { } ''
          mkdir $out
          cp -r ${path}/* $out
          mkdir -p $out/machines/testmachine

          # TODO: Instead create a machine by calling the API, this wont break in future tests and is much closer to what the user performs
          cat > $out/machines/testmachine/hardware-configuration.nix << EOF
          { lib, ... }: {
            nixpkgs.hostPlatform = "x86_64-linux";
            system.stateVersion = lib.version;
            documentation.enable = false;
            users.users.root.initialPassword = "fnord23";
            boot.loader.grub.devices = lib.mkForce [ "/dev/sda" ];
            fileSystems."/".device = lib.mkDefault "/dev/sda";
          }
          EOF
        '';
        evaled = (import "${initialized}/flake.nix").outputs {
          self = evaled // {
            outPath = initialized;
          };
          clan-core = self;
        };
      in
      {
        type = "derivation";
        name = "minimal-clan-flake-check";
        inherit (evaled.nixosConfigurations.testmachine.config.system.build.toplevel) drvPath outPath;
      };
  };
}
