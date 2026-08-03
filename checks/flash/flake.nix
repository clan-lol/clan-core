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

      machineFor =
        system:
        { lib, ... }:
        {
          # We need to use `mkForce` because we inherit from `test-install-machine`
          # which currently hardcodes `nixpkgs.hostPlatform`
          nixpkgs.hostPlatform = lib.mkForce system;

          imports = [ (import ./installation-machine.nix { inherit clan-core; }) ];

          clan.core.networking.targetHost = "test-flash-machine";

          # The flash child flake is stored in /nix/store, so we can't run
          # generators at eval time.
          clan.core.settings.state-version.enable = false;
          clan.core.vars.generators.test-partitioning = lib.mkForce { };
          disko.devices.disk.main.preCreateHook = lib.mkForce "";

          # Every option here should match the options set through `clan flash write`
          # if you get a mass rebuild on the disko derivation, this means you need to
          # adjust something here. Also make sure that the injected json in clan flash write
          # is up to date.
          i18n.defaultLocale = "de_DE.UTF-8";
          console.keyMap = "de";
          services.xserver.xkb.layout = "de";
          users.users.root.openssh.authorizedKeys.keys = [
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRWUusawhlIorx7VFeQJHmMkhl9X3QpnvOdhnV/bQNG root@target\n"
          ];
        };

      machines = lib.listToAttrs (
        map (system: lib.nameValuePair "test-flash-machine-${system}" (machineFor system)) linuxSystems
      );

      clan = clan-core.lib.clan {
        inherit self;
        inherit machines;

        inventory = {
          meta.name = "test-flash";
          machines = lib.mapAttrs (_: _: { }) machines;
        };
      };
    in
    {
      inherit (clan.config) nixosConfigurations nixosModules clanInternals;
    };
}
