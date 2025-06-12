{
  pkgs,
  nixosLib,
  clan-core,
  ...
}:

nixosLib.runTest (
  { ... }:
  {
    imports = [
      clan-core.modules.nixosVmTest.clanTest
    ];

    hostPkgs = pkgs;

    name = "state-version";

    clan = {
      directory = ./.;
      modules."@clan/state-version" = ../../default.nix;
      inventory = {
        machines.server = { };
        instances.default = {
          module.name = "@clan/state-version";
          roles.default.machines."server" = { };
        };
      };
    };

    nodes.server = { };

    testScript = ''
      start_all()
    '';
  }
)
