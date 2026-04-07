{
  name = "users";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };

      instances = {
        root-password-test = {
          module.name = "@clan/users";
          module.input = "self";
          roles.default.machines."server".settings = {
            user = "root";
            prompt = false;
          };
        };
        user-password-test = {
          module.name = "@clan/users";
          module.input = "self";
          roles.default.machines."server".settings = {
            user = "testuser";
            prompt = false;
            openssh.authorizedKeys = {
              keys = [
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKInlineTestKey00000000000000000000000000000000 inline@test"
              ];
              keyFiles = [
                ./test_key.pub
              ];
            };
          };
        };
      };
    };
  };

  nodes = {
    server = {
      services.openssh.enable = true;
      users.users.testuser.group = "testuser";
      users.groups.testuser = { };
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

    # Check that inline authorizedKeys.keys are present
    server.succeed("grep 'inline@test' /etc/ssh/authorized_keys.d/testuser")

    # Check that authorizedKeys.keyFiles content is present
    server.succeed("grep 'keyfile@test' /etc/ssh/authorized_keys.d/testuser")

  '';
}
