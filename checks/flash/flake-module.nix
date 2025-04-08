{
  config,
  self,
  lib,
  ...
}:
{
  clan.machines = lib.listToAttrs (
    lib.map (
      system:
      lib.nameValuePair "test-flash-machine-${system}" {
        clan.core.networking.targetHost = "test-flash-machine";
        fileSystems."/".device = lib.mkDefault "/dev/vda";
        boot.loader.grub.device = lib.mkDefault "/dev/vda";

        # We need to use `mkForce` because we inherit from `test-install-machine`
        # which currently hardcodes `nixpkgs.hostPlatform`
        nixpkgs.hostPlatform = lib.mkForce system;

        imports = [ self.nixosModules.test-flash-machine ];
      }
    ) (lib.filter (lib.hasSuffix "linux") config.systems)
  );

  flake.nixosModules = {
    test-flash-machine =
      { lib, ... }:
      {
        imports = [ self.nixosModules.test-install-machine ];

        clan.core.vars.generators.test = lib.mkForce { };

        disko.devices.disk.main.preCreateHook = lib.mkForce "";
      };
  };

  perSystem =
    {
      pkgs,
      lib,
      ...
    }:
    let
      dependencies = [
        pkgs.disko
        self.nixosConfigurations."test-flash-machine-${pkgs.hostPlatform.system}".pkgs.perlPackages.ConfigIniFiles
        self.nixosConfigurations."test-flash-machine-${pkgs.hostPlatform.system}".pkgs.perlPackages.FileSlurp

        self.nixosConfigurations."test-flash-machine-${pkgs.hostPlatform.system}".config.system.build.toplevel
        self.nixosConfigurations."test-flash-machine-${pkgs.hostPlatform.system}".config.system.build.diskoScript
        self.nixosConfigurations."test-flash-machine-${pkgs.hostPlatform.system}".config.system.build.diskoScript.drvPath
        self.nixosConfigurations."test-flash-machine-${pkgs.hostPlatform.system}".config.system.clan.deployment.file

      ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
      closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
    in
    {
      checks = pkgs.lib.mkIf pkgs.stdenv.isLinux {
        test-flash = (import ../lib/test-base.nix) {
          name = "flash";
          nodes.target = {
            virtualisation.emptyDiskImages = [ 4096 ];
            virtualisation.memorySize = 3000;
            environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
            environment.etc."install-closure".source = "${closureInfo}/store-paths";

            nix.settings = {
              substituters = lib.mkForce [ ];
              hashed-mirrors = null;
              connect-timeout = lib.mkForce 3;
              flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
              experimental-features = [
                "nix-command"
                "flakes"
              ];
            };
          };
          testScript = ''
            start_all()

            # Some distros like to automount disks with spaces
            machine.succeed('mkdir -p "/mnt/with spaces" && mkfs.ext4 /dev/vdb && mount /dev/vdb "/mnt/with spaces"')
            machine.succeed("clan flash write --debug --flake ${../..} --yes --disk main /dev/vdb test-flash-machine-${pkgs.hostPlatform.system}")
          '';
        } { inherit pkgs self; };
      };
    };
}
