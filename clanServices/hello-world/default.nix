# Example clan service. See https://docs.clan.lol/guides/services/community/
# for more details

# The test for this module in ./tests/vm/default.nix shows an example of how
# the service is used.

{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/hello-word";
  manifest.description = "Minimal example clan service that greets the world";
  manifest.readme = builtins.readFile ./README.md;

  # This service provides two roles: "morning" and "evening". Roles can be
  # defined in this file directly (e.g. the "morning" role) or split up into a
  # separate file (e.g. the "evening" role)
  roles.morning = {
    description = "A morning greeting machine";
    interface =
      { lib, ... }:
      {
        # Here we define the settings for this role. They will be accessible
        # via `roles.morning.settings` in the role

        options.greeting = lib.mkOption {
          type = lib.types.str;
          default = "Good morning";
          description = "The greeting to use";
        };
      };
    # Maps over all instances and produces one result per instance.
    perInstance =
      {
        # Role settings for this machine/instance
        settings,

        # The name of this instance of the service
        instanceName,

        # The current machine
        machine,

        # All roles of this service, with their assigned machines
        roles,
        ...
      }:
      {
        # Analog to 'perSystem' of flake-parts.
        # For every instance of this service we will add a nixosModule to a morning-machine
        nixosModule =
          { ... }:
          {
            # Interaction examples what you could do here:
            # - Get some settings of this machine
            # settings.ipRanges
            #
            # - Get all evening names:
            # allEveningNames = lib.attrNames roles.evening.machines
            #
            # - Get all roles of the machine:
            # machine.roles
            #
            # - Get the settings that where applied to a specific evening machine:
            # roles.evening.machines.peer1.settings
            imports = [ ];
            environment.etc.hello.text = "${settings.greeting} World!";
          };
      };
  };

  # The implementation of the evening role is in a separate file. We have kept
  # the interface here, so we can see all settings of the service in one place,
  # but you can also move it to the respective file
  roles.evening = {
    description = "An evening greeting machine";
    interface =
      { lib, ... }:
      {
        options.greeting = lib.mkOption {
          type = lib.types.str;
          default = "Good evening";
          description = "The greeting to use";
        };
      };
  };
  imports = [ ./evening.nix ];

  # This part gets applied to all machines, regardless of their role.
  perMachine =
    { machine, ... }:
    {
      nixosModule =
        { pkgs, ... }:
        {
          environment.systemPackages = [
            (pkgs.writeShellScriptBin "greet-world" ''
              #!${pkgs.bash}/bin/bash
              set -euo pipefail

              cat /etc/hello
              echo " I'm ${machine.name}"
            '')
          ];
        };
    };
}
