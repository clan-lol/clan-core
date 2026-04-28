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
      nixpkgs,
      systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;

      linuxSystems = lib.filter (lib.hasSuffix "linux") (import systems);

      # Same key pair as in pkgs/clan-cli/clan_cli/tests/age_keys.py.
      # Inlined here because the child flake cannot read sibling asset
      # directories and the wrapper used to set this from the parent flake.
      ageRecipient = "age1dhwqzkah943xzc34tc3dlmfayyevcmdmxzjezdgdy33euxwf59vsp3vk3c";

      installationMachine = import ./installation-machine.nix { inherit clan-core; };

      # Activation override shared by the age and password-store variants.
      # Their secret backends place activation secrets under
      # /etc/secret-vars/activation/ instead of the sops default
      # /var/lib/sops-nix/activation/.
      etcSecretVarsActivation =
        { lib, ... }:
        {
          system.activationScripts.test-vars-activation.text = lib.mkForce ''
            test -e /etc/secret-vars/activation/test-activation/test || {
              echo "\nTEST ERROR: Activation secret not found!\n" >&2
              exit 1
            }
          '';
        };

      # Variants of the without-system base machine. These do not pre-bake a
      # facter report; the test runs `clan machines init-hardware-config`
      # against them to materialise hardware data inside the sandbox.
      withoutSystemBase = {
        nixpkgs.hostPlatform = lib.head linuxSystems;
        imports = [ installationMachine ];
      };

      withoutSystemMachines = {
        test-install-machine-without-system = withoutSystemBase;

        test-install-machine-without-system-with-age =
          { lib, ... }:
          {
            clan.core.vars.settings.secretStore = lib.mkForce "age";
            # clan-core itself is a sops clan; disabling the consistency
            # check lets the test machines opt into a different backend
            # without tripping cross-check assertions against clan-core.
            clan.core.vars.enableConsistencyCheck = false;
            imports = [
              installationMachine
              etcSecretVarsActivation
            ];
            nixpkgs.hostPlatform = lib.head linuxSystems;
          };

        test-install-machine-without-system-with-password-store =
          { lib, ... }:
          {
            clan.core.vars.settings.secretStore = lib.mkForce "password-store";
            clan.core.vars.enableConsistencyCheck = false;
            imports = [
              installationMachine
              etcSecretVarsActivation
            ];
            nixpkgs.hostPlatform = lib.head linuxSystems;
          };
      };

      # Per-system pre-built variants. Their toplevels are pulled into
      # closureInfo so the in-test `clan machines install` step (with
      # nixos-facter) does not have to rebuild from source.
      perSystemMachines = lib.listToAttrs (
        lib.concatMap (system: [
          {
            name = "test-install-machine-${system}";
            value = {
              hardware.facter.reportPath = import ./facter-report.nix system;
              nixpkgs.hostPlatform = system;
              imports = [ installationMachine ];
            };
          }
          {
            name = "test-install-machine-age-${system}";
            value =
              { lib, ... }:
              {
                hardware.facter.reportPath = import ./facter-report.nix system;
                clan.core.vars.settings.secretStore = lib.mkForce "age";
                clan.core.vars.enableConsistencyCheck = false;
                nixpkgs.hostPlatform = system;
                imports = [ installationMachine ];
              };
          }
        ]) linuxSystems
      );

      machines = withoutSystemMachines // perSystemMachines;

      clan = clan-core.lib.clan {
        inherit self;
        inherit machines;
        vars.settings.recipients.hosts.test-install-machine-without-system-with-age = [
          ageRecipient
        ];
        inventory = {
          meta.name = "test-installation";
          meta.domain = "test-installation";
          machines = lib.mapAttrs (_: _: { }) machines;
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
