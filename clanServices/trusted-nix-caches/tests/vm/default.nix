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

    name = "trusted-nix-caches";

    clan = {
      directory = ./.;
      modules."@clan/trusted-nix-caches" = ../../default.nix;
      inventory = {
        machines.server = { };

        instances = {
          trusted-nix-caches = {
            module.name = "@clan/trusted-nix-caches";
            roles.default.machines."server" = { };
          };
        };
      };
    };

    nodes.server = { };

    testScript = ''
      start_all()
      server.succeed("grep -q 'cache.clan.lol' /etc/nix/nix.conf")
    '';
  }
)
