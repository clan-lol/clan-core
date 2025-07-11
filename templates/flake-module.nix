{ self, inputs, ... }:
{
  clan = {
    inherit (((import ./flake.nix).outputs { }).clan) templates;
  };

  flake = {
    checks.x86_64-linux.equal-templates =
      inputs.nixpkgs.legacyPackages.x86_64-linux.runCommand "minimal-clan-flake" { }
        ''
          file1=${./clan/default/clan.nix}
          file2=${./clan/flake-parts/clan.nix}

          echo "Comparing $file1 and $file2"
          if cmp -s "$file1" "$file2"; then
            echo "clan.nix files are identical"
          else
            echo "clan.nix files are out of sync"
            echo "Please make sure to keep templates clan.nix files in sync."
            echo "files: templates/clan/default/clan.nix templates/clan/flake-parts/clan.nix"
            echo "--------------------------------\n"
            diff "$file1" "$file2"
            echo "--------------------------------\n\n"
            exit 1
          fi

          touch $out
        '';
    checks.x86_64-linux.template-minimal =
      let
        path = self.clan.templates.clan.minimal.path;
        initialized = inputs.nixpkgs.legacyPackages.x86_64-linux.runCommand "minimal-clan-flake" { } ''
          mkdir $out
          cp -r ${path}/* $out
          mkdir -p $out/machines/testmachine

          # TODO: Instead create a machine by calling the API, this wont break in future tests and is much closer to what the user performs
          cat > $out/machines/testmachine/hardware-configuration.nix << EOF
          { lib, config, ... }: {
            nixpkgs.hostPlatform = "x86_64-linux";
            system.stateVersion = config.system.nixos.release;
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
