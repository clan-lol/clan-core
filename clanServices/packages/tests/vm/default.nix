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

    name = "packages";

    clan = {
      directory = ./.;
      modules."@clan/packages" = ../../default.nix;
      inventory = {
        machines.server = { };

        instances.default = {
          module.name = "@clan/packages";
          roles.default.machines."server".settings = {
            packages = [ "cbonsai" ];
          };
        };
      };
    };

    nodes.server = { };

    testScript = ''
      start_all()
      server.succeed("cbonsai")
    '';
  }
)
