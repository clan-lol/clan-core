{ lib, clanLib }:
let
  clan = clanLib.clan {
    self = { };
    directory = ./.;

    machines.jon = { };
    machines.sara = { };
    # A module that adds exports perMachine
    modules.A =
      { ... }:
      {
        manifest.name = "A";
        roles.peer.perInstance =
          { ... }:
          {
            nixosModule = {
              options.bar = lib.mkOption {
                default = 1;
              };
            };
          };
        roles.server = { };
        perMachine =
          { ... }:
          {
            nixosModule = {
              options.foo = lib.mkOption {
                default = 1;
              };
            };
          };
      };
    inventory.instances.A = {
      module.input = "self";
      roles.peer.tags.all = { };
    };
  };
in
{
  test_1 = {
    inherit clan;
    expr = { inherit (clan.config.clanInternals.machines.x86_64-linux.jon.config) bar foo; };
    expected = {
      foo = 1;
      bar = 1;
    };
  };
}
