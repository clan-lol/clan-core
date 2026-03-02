{
  inputs.clan-core.url = "https://__replace__";
  inputs.nixpkgs.url = "https://__replace__";
  inputs.clan-core.inputs.nixpkgs.follows = "nixpkgs";
  inputs.systems.url = "https://__systems__";
  inputs.systems.flake = false;

  outputs =
    {
      self,
      clan-core,
      systems,
      ...
    }:
    let

      # Usage see: https://docs.clan.lol
      clan = clan-core.lib.clan {
        inherit self;

        machines.test-update-machine =
          {
            lib,
            modulesPath,
            ...
          }:
          {
            imports = [
              ./test-update-machine/configuration.nix
              (modulesPath + "/testing/test-instrumentation.nix")
              (modulesPath + "/profiles/qemu-guest.nix")
              clan-core.clanLib.test.minifyModule
              (clan-core + "/lib/test/container-test-driver/nixos-module.nix")
            ];
            nixpkgs.hostPlatform = lib.head (import systems);

            # Apply patch to fix x-initrd.mount filesystem handling in switch-to-configuration-ng
            # Currently maintained at https://github.com/Enzime/nixpkgs/tree/switch-to-configuration-ng-container-tests
            nixpkgs.overlays = [
              (_final: prev: {
                switch-to-configuration-ng = prev.switch-to-configuration-ng.overrideAttrs (old: {
                  patches = (old.patches or [ ]) ++ [
                    (prev.fetchpatch {
                      url = "file://${./switch-to-configuration-initrd-mount-fix.patch}";
                      hash = "sha256-iKmgZDUd4DkHa7MPuaZX6h85+0Nc4lY+w1YRBIwwQt0=";
                      relative = "pkgs/by-name/sw/switch-to-configuration-ng/src";
                    })
                  ];
                });
              })
            ];

            networking.hostName = "update-machine";

            environment.etc."install-successful".text = "ok";

            # Enable SSH and add authorized key for testing
            services.openssh.enable = true;
            services.openssh.settings.PasswordAuthentication = false;
            users.users.root.openssh.authorizedKeys.keys = [
              (builtins.readFile (clan-core + "/checks/assets/ssh/pubkey"))
            ];
            services.openssh.knownHosts.localhost.publicKeyFile = (clan-core + "/checks/assets/ssh/pubkey");
            services.openssh.hostKeys = [
              {
                path = "/run/ssh-hostkey/privkey";
                type = "ed25519";
              }
            ];
            systemd.tmpfiles.settings."10-ssh-hostkey" = {
              "/run/ssh-hostkey".d = {
                mode = "0700";
                user = "root";
                group = "root";
              };
              "/run/ssh-hostkey/privkey"."C+" = {
                argument = "${lib.cleanSource "${clan-core}/checks/assets/ssh/privkey"}";
                mode = "0600";
                user = "root";
                group = "root";
              };
            };
            security.sudo.wheelNeedsPassword = false;

            boot.consoleLogLevel = lib.mkForce 100;
            boot.kernelParams = [ "boot.shell_on_fail" ];

            boot.isContainer = true;
            # Preserve the IP addresses assigned by the test framework
            # (based on virtualisation.vlans = [1] and node number 1)
            networking.interfaces.eth1 = {
              useDHCP = false;
              ipv4.addresses = [
                {
                  address = "192.168.1.1";
                  prefixLength = 24;
                }
              ];
              ipv6.addresses = [
                {
                  address = "2001:db8:1::1";
                  prefixLength = 64;
                }
              ];
            };

            nix.settings = {
              flake-registry = "";
              # required for setting the `flake-registry`
              experimental-features = [
                "nix-command"
                "flakes"
              ];
              # Disable substituters to speed up tests
              substituters = lib.mkForce [ ];
            };

            # Define the mounts that exist in the container to prevent them from being stopped
            fileSystems = {
              "/" = {
                device = "/dev/disk/by-label/nixos";
                fsType = "ext4";
                options = [ "x-initrd.mount" ];
              };
              "/nix/.rw-store" = {
                device = "tmpfs";
                fsType = "tmpfs";
                options = [
                  "mode=0755"
                ];
              };
              "/nix/store" = {
                device = "overlay";
                fsType = "overlay";
                options = [
                  "lowerdir=/nix/.ro-store"
                  "upperdir=/nix/.rw-store/upper"
                  "workdir=/nix/.rw-store/work"
                ];
              };
            };
          };

        inventory =
          { ... }:
          {
            meta.name = "foo";
            meta.domain = "foo";
            machines.test-update-machine = { };
          };
      };
    in
    {
      # all machines managed by Clan
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
