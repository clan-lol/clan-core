(import ../lib/container-test.nix) ({ ... }: {
  name = "borgbackup";

  nodes.machine = { self, ... }: {
    imports = [
      self.clanModules.borgbackup
      self.nixosModules.clanCore
      {
        services.openssh.enable = true;
        services.borgbackup.repos.testrepo = {
          authorizedKeys = [
            (builtins.readFile ./borg_test.pub)
          ];
        };
      }
      {
        clanCore.machineName = "machine";
        clanCore.clanDir = ./.;
        clanCore.state.testState.folders = [ "/etc/state" ];
        environment.etc.state.text = "hello world";
        clan.borgbackup = {
          enable = true;
          destinations.test = {
            repo = "borg@localhost:.";
            rsh = "ssh -i ${./borg_test} -o StrictHostKeyChecking=no";
          };
        };
      }
    ];
  };
  testScript = ''
    start_all()
    machine.systemctl("start --wait borgbackup-job-test.service")
    assert "machine-test" in machine.succeed("BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK=yes /run/current-system/sw/bin/borg-job-test list")
  '';
})
