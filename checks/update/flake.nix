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

      # Usage see: https://clan.lol/docs
      clan = clan-core.lib.clan {
        inherit self;

        machines.machine =
          {
            lib,
            options,
            modulesPath,
            ...
          }:
          {
            imports = [
              ./machine/configuration.nix
              (modulesPath + "/testing/test-instrumentation.nix")
              (modulesPath + "/profiles/qemu-guest.nix")
              clan-core.clanLib.test.minifyModule
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
                      hash = "sha256-Zd3dtu07W3OQFqQ218SUxM11ME4jdG4B59UAIoqsVGc=";
                      relative = "pkgs/by-name/sw/switch-to-configuration-ng";
                    })
                  ];
                });
              })
            ];

            networking.hostName = "machine";

            environment.etc."install-successful".text = "ok";

            # Pre-seed a switch inhibitor so the VM test can trigger a
            # blocking inhibitor change by deploying a different value.
            system.switch.inhibitors.test-component = "original";

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

            # Container sandbox workarounds. These are also applied by the test
            # framework's containerDefaults at boot, but must be baked into the
            # machine's own config so the system that `clan machines update`
            # rebuilds and switches to keeps working inside the nspawn sandbox.
            console.enable = true;
            system.build.initialRamdisk = "";
            virtualisation = lib.optionalAttrs (options ? virtualisation.sharedDirectories) {
              sharedDirectories = lib.mkForce { };
            };
            networking.useDHCP = false;
            services.openssh.settings.UsePAM = false;
            networking.useNetworkd = true;
            networking.useHostResolvConf = false;
            services.resolved.enable = false;
            systemd.services.backdoor.enable = false;
            systemd.services.nix-daemon.serviceConfig.CPUSchedulingPolicy = lib.mkForce "";
            systemd.services.suid-sgid-wrappers.enable = false;
            systemd.services.resolvconf.enable = false;
            programs.ssh.systemd-ssh-proxy.enable = false;

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
            machines.machine = { };
          };
      };
    in
    {
      # all machines managed by Clan
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
