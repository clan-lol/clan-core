{
  ...
}:
{
  name = "data-mesher";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {

      machines.alpha = { };
      machines.beta = { };
      machines.gamma = { };

      instances.data-mesher = {
        roles.default.tags = [ "all" ];

        roles.default.extraModules = [
          (
            { lib, ... }:
            {
              services.data-mesher.settings = {
                # reduce these intervals to speed up the test
                cluster.join_interval = lib.mkForce "2s";
                cluster.push_pull_interval = lib.mkForce "5s";
              };
            }
          )
        ];

        roles.default.settings = {

          files = {
            "test_file" = [
              "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww=" # admin
            ];
          };

          network.interface = "eth1";

          bootstrapNodes = [
            "[2001:db8:1::1]:7946" # alpha
            "[2001:db8:1::2]:7946" # beta
            "[2001:db8:1::3]:7946" # gamma
          ];

        };
      };

    };
  };

  nodes = { };

  testScript = ''
    def upload_file(node, filename, content, key_path="${./admin.key}"):
        """Create a file and upload it via the cli"""
        node.succeed(f"echo -n '{content}' > /tmp/{filename}")
        node.succeed(f"data-mesher file update /tmp/{filename} --url http://[::1]:7331 --key-path {key_path}")

    def wait_for_file(node, filename, expected_content, timeout=60):
        """Wait until a file exists with the expected content"""
        node.wait_until_succeeds(
            f"test -f /var/lib/data-mesher/files/{filename} && "
            f"grep -q '{expected_content}' /var/lib/data-mesher/files/{filename}",
            timeout
        )

    def delete_file(node, filename, key_path="${./admin.key}"):
        """Delete a file via the cli (creates a tombstone)"""
        node.succeed(f"data-mesher file delete {filename} --url http://[::1]:7331 --key-path {key_path}")

    def wait_for_file_deleted(node, filename, timeout=60):
        """Wait until a file no longer exists"""
        node.wait_until_succeeds(
            f"test ! -f /var/lib/data-mesher/files/{filename}",
            timeout
        )

    start_all()

    for node in [alpha, beta, gamma]:
        # Verify services starts
        node.wait_for_unit("data-mesher.service")

        # Verify the config was generated with our settings
        node.succeed("grep 'eth1' /etc/data-mesher/dm.toml")
        node.succeed("grep 'test_file' /etc/data-mesher/dm.toml")

    # Upload a file
    upload_file(alpha, "test_file", "hello world")

    # Check that it propagated
    for node in [alpha, beta, gamma]:
        wait_for_file(node, "test_file", "hello world")

    # Delete the file
    delete_file(beta, "test_file")

    # Check the tombstone propagates
    for node in [alpha, beta, gamma]:
        wait_for_file_deleted(node, "test_file")
  '';
}
