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
          network.files = {
            "test_file" = [
              "azwT+VhTxA+BF73Hwq0uqdXHG8XvHU2BknoVXgmEjww=" # admin
            ];
          };
          network.namespaces = [ "test_ns" ];
        };

        roles.bootstrap.machines = {
          alpha = { };
          beta = { };
        };
      };

    };
  };

  nodes = { };

  testScript =
    { nodes, ... }:
    let
      networkID = nodes.alpha.clan.core.vars.generators.data-mesher-network.files."network.pub".path;
      alphaIdentityKey =
        nodes.alpha.clan.core.vars.generators.data-mesher-node-identity.files."identity.key".path;
      alphaIdentityCert =
        nodes.alpha.clan.core.vars.generators.data-mesher-node-identity.files."identity.cert".path;
      alphaIdentityPub =
        nodes.alpha.clan.core.vars.generators.data-mesher-node-identity.files."identity.pub".path;
    in
    ''
      import base64
      import subprocess

      def upload_file(node, filename, content, key_path="${./admin.key}"):
          """Create a file and upload it via the cli"""
          node.succeed(f"echo -n '{content}' > /tmp/{filename}")
          node.succeed(f"data-mesher file update /tmp/{filename} --network-id ${networkID} --url http://[::1]:7331 --key {key_path}")

      def wait_for_file(node, filename, expected_content, timeout=60):
          """Wait until a file exists with the expected content"""
          node.wait_until_succeeds(
              f"test -f /var/lib/data-mesher/files/home/{filename} && "
              f"grep -q '{expected_content}' /var/lib/data-mesher/files/home/{filename}",
              timeout
          )

      def delete_file(node, filename, key_path="${./admin.key}"):
          """Delete a file via the cli (creates a tombstone)"""
          node.succeed(f"data-mesher file delete {filename} --network-id ${networkID} --url http://[::1]:7331 --key {key_path}")

      def wait_for_file_deleted(node, filename, timeout=60):
          """Wait until a file no longer exists"""
          node.wait_until_succeeds(
              f"test ! -f /var/lib/data-mesher/files/home/{filename}",
              timeout
          )

      start_all()

      for node in [alpha, beta, gamma]:
          # Verify services starts
          node.wait_for_unit("data-mesher.service")

      # ===== Test 1: Static file upload and propagation =====
      upload_file(alpha, "test_file", "hello world")

      for node in [alpha, beta, gamma]:
          wait_for_file(node, "test_file", "hello world")

      # ===== Test 2: File deletion =====
      delete_file(beta, "test_file")

      for node in [alpha, beta, gamma]:
          wait_for_file_deleted(node, "test_file")

      # ===== Test 3: Namespace file upload and propagation =====
      # Get alpha's identity pubkey and compute its URL-encoded form for the namespace path
      alpha_pub_pem = alpha.succeed("cat ${alphaIdentityPub}").strip()
      # Extract the base64 key from PEM, decode to raw bytes, re-encode as base64url unpadded
      pem_lines = [l for l in alpha_pub_pem.splitlines() if not l.startswith("-----")]
      import base64 as b64
      der_bytes = b64.b64decode("".join(pem_lines))
      raw_key = der_bytes[-32:]  # ED25519 PKIX DER: last 32 bytes
      url_key = b64.urlsafe_b64encode(raw_key).rstrip(b"=").decode()

      ns_filename = f"test_ns/{url_key}"
      alpha.succeed(f"echo -n 'namespace_data' > /tmp/ns_file")
      alpha.succeed(
          f"data-mesher file update /tmp/ns_file"
          f" --name '{ns_filename}'"
          f" --url http://[::1]:7331"
          f" --key ${alphaIdentityKey}"
          f" --network-id ${networkID}"
          f" --cert ${alphaIdentityCert}"
      )

      # Verify namespace file propagates to all nodes
      for node in [alpha, beta, gamma]:
          wait_for_file(node, ns_filename, "namespace_data")

      # ===== Test 4: Namespace rejection without certificate =====
      # Uploading without --cert should fail
      alpha.succeed("echo -n 'no_cert' > /tmp/ns_nocert")
      alpha.fail(
          f"data-mesher file update /tmp/ns_nocert"
          f" --name '{ns_filename}'"
          f" --url http://[::1]:7331"
          f" --key ${alphaIdentityKey}"
          f" --network-id ${networkID}"
      )
    '';
}
