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
            modulesPath,
            ...
          }:
          {
            imports = [
              ./machine/configuration.nix
              (modulesPath + "/testing/test-instrumentation.nix")
              (modulesPath + "/profiles/qemu-guest.nix")
              (modulesPath + "/virtualisation/qemu-vm.nix")
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

            services.openssh.ports = [
              22
              2222
            ];
            virtualisation.forwardPorts = [
              {
                from = "host";
                host.port = 2222;
                guest.port = 2222;
              }
            ];
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

            boot.loader.grub.enable = false;

            virtualisation.memorySize = 4096;
            virtualisation.cores = 2;

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
