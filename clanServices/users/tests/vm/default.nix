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

    name = "users";

    clan = {
      directory = ./.;
      modules."@clan/users" = ../../default.nix;
      inventory = {
        machines.server = { };

        instances = {
          root-password-test = {
            module.name = "@clan/users";
            roles.default.machines."server".settings = {
              user = "root";
              prompt = false;
            };
          };
          user-password-test = {
            module.name = "@clan/users";
            roles.default.machines."server".settings = {
              user = "testuser";
              prompt = false;
            };
          };
        };
      };
    };

    nodes = {
      server = {
        users.users.testuser.group = "testuser";
        users.groups.testuser = { };
        users.users.testuser.isNormalUser = true;
      };
    };

    testScript = ''
      start_all()

      server.wait_for_unit("multi-user.target")

      # Check that the testuser account exists
      server.succeed("id testuser")

      # Try to log in as the user using the generated password
      # TODO: fix
      # password = server.succeed("cat /run/clan/vars/user-password/user-password").strip()
      # server.succeed(f"echo '{password}' | su - testuser -c 'echo Login successful'")

    '';
  }
)
