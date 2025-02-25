{ self, inputs, ... }:
{
  clan.templates = {
    disko = {
      single-disk = {
        description = "A simple ext4 disk with a single partition";
        path = ./disk/single-disk;
      };
    };

    machine = {
      flash-installer = {
        description = "Initialize a new flash-installer machine";
        path = ./machine/flash-installer;
      };

      new-machine = {
        description = "Initialize a new machine";
        path = ./machine/new-machine;
      };
    };

    clan = {
      default = {
        description = "Initialize a new clan flake";
        path = ./clan/new-clan;
      };
      minimal = {
        description = "for clans managed via (G)UI";
        path = ./clan/minimal;
      };
      flake-parts = {
        description = "Flake-parts";
        path = ./clan/flake-parts;
      };
      minimal-flake-parts = {
        description = "Minimal flake-parts clan template";
        path = ./clan/minimal-flake-parts;
      };
    };
  };

  flake = {
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
