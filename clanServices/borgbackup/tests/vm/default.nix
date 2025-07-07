{
  pkgs,
  ...
}:
{
  name = "service-borgbackup";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {

      machines.clientone = { };
      machines.serverone = { };

      instances = {
        borgone = {

          module.name = "@clan/borgbackup";
          module.input = "self";

          roles.client.machines."clientone" = { };
          roles.server.machines."serverone".settings.directory = "/tmp/borg-test";
        };
      };
    };
  };

  nodes = {

    serverone = {
      services.openssh.enable = true;
      # Needed so PAM doesn't see the user as locked
      users.users.borg.password = "borg";
    };

    clientone =
      {
        config,
        pkgs,
        clan-core,
        ...
      }:
      {

        services.openssh.enable = true;

        users.users.root.openssh.authorizedKeys.keyFiles = [ ../../../../checks/assets/ssh/pubkey ];

        clan.core.networking.targetHost = config.networking.hostName;

        environment.systemPackages = [ clan-core.packages.${pkgs.system}.clan-cli ];

        clan.core.state.test-backups.folders = [ "/var/test-backups" ];
      };

  };

  testScript = ''
    import json
    start_all()

    machines = [clientone, serverone]

    for m in machines:
        m.systemctl("start network-online.target")

    for m in machines:
        m.wait_for_unit("network-online.target")

    # dummy data
    clientone.succeed("mkdir -p /var/test-backups /var/test-service")
    clientone.succeed("echo testing > /var/test-backups/somefile")

    clientone.succeed("${pkgs.coreutils}/bin/install -Dm 600 ${../../../../checks/assets/ssh/privkey} /root/.ssh/id_ed25519")
    clientone.succeed("${pkgs.coreutils}/bin/touch /root/.ssh/known_hosts")
    clientone.wait_until_succeeds("timeout 2 ssh -o StrictHostKeyChecking=accept-new localhost hostname")
    clientone.wait_until_succeeds("timeout 2 ssh -o StrictHostKeyChecking=accept-new $(hostname) hostname")

    # create
    clientone.succeed("borgbackup-create >&2")
    clientone.wait_until_succeeds("! systemctl is-active borgbackup-job-serverone >&2")

    # list
    backup_id = json.loads(clientone.succeed("borg-job-serverone list --json"))["archives"][0]["archive"]
    out = clientone.succeed("borgbackup-list").strip()
    print(out)
    assert backup_id in out, f"backup {backup_id} not found in {out}"

    # borgbackup restore
    clientone.succeed("rm -f /var/test-backups/somefile")
    clientone.succeed(f"NAME='serverone::borg@serverone:.::{backup_id}' borgbackup-restore >&2")
    assert clientone.succeed("cat /var/test-backups/somefile").strip() == "testing", "restore failed"
  '';
}
