{
  name = "trusted-nix-caches";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };

      instances = {
        trusted-nix-caches = {
          module.name = "@clan/trusted-nix-caches";
          module.input = "self";
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
