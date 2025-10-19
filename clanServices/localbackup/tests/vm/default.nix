{ ... }:
{
  name = "localbackup";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {

      machines.machine = { };

      instances = {
        localbackup = {
          module.name = "@clan/localbackup";
          module.input = "self";
          roles.default.machines."machine".settings = {

            targets.hdd = {
              directory = "/mnt/external-disk";
              preMountHook = ''
                touch /run/mount-external-disk
              '';
              postUnmountHook = ''
                touch /run/unmount-external-disk
              '';
            };
          };
        };
      };
    };
  };

  nodes.machine = {
    clan.core.state.test-backups.folders = [ "/var/test-backups" ];
  };

  testScript = ''
    import json
    start_all()

    machine.systemctl("start network-online.target")
    machine.wait_for_unit("network-online.target")

    # dummy data
    machine.succeed("mkdir -p /var/test-backups")
    machine.succeed("echo testing > /var/test-backups/somefile")

    # create
    machine.succeed("localbackup-create >&2")
    machine.wait_until_succeeds("! systemctl is-active localbackup-job-serverone >&2")

    # list
    snapshot_list = machine.succeed("localbackup-list").strip()
    assert json.loads(snapshot_list)[0]["name"].strip() == "hdd::/mnt/external-disk/snapshot.0"

    # borgbackup restore
    machine.succeed("rm -f /var/test-backups/somefile")

    machine.succeed("NAME=/mnt/external-disk/snapshot.0 FOLDERS=/var/test-backups /run/current-system/sw/bin/localbackup-restore >&2")
    assert machine.succeed("cat /var/test-backups/somefile").strip() == "testing", "restore failed"
  '';
}
