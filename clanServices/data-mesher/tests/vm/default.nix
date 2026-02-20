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
                log_level = lib.mkForce "debug";
                # reduce this interval to speed up the test
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
        };

        roles.bootstrap.machines = {
          alpha = { };
          beta = { };
        };
      };

    };
  };

  nodes = { };

  testScript = ''
    def upload_file(node, filename, content, key_path="${./admin.key}"):
        """Create a file and upload it via the cli"""
        node.succeed(f"echo -n '{content}' > /tmp/{filename}")
        node.succeed(f"data-mesher file update /tmp/{filename} --url http://[::1]:7331 --key {key_path}")

    def wait_for_file(node, filename, expected_content, timeout=60):
        """Wait until a file exists with the expected content"""
        node.wait_until_succeeds(
            f"test -f /var/lib/data-mesher/files/{filename} && "
            f"grep -q '{expected_content}' /var/lib/data-mesher/files/{filename}",
            timeout
        )

    def delete_file(node, filename, key_path="${./admin.key}"):
        """Delete a file via the cli (creates a tombstone)"""
        node.succeed(f"data-mesher file delete {filename} --url http://[::1]:7331 --key {key_path}")

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
