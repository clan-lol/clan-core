(import ../lib/test-base.nix) ({ ... }: {
  name = "borgbackup";

  nodes.machine = { self, ... }: {
    imports = [
      self.clanModules.borgbackup
      self.nixosModules.clanCore
      {
        services.openssh.enable = true;
        services.borgbackup.repos.testrepo = {
          authorizedKeys = [
            (builtins.readFile ../lib/ssh/pubkey)
          ];
        };
      }
      {
        clanCore.machineName = "machine";
        clanCore.clanDir = ./.;
        clanCore.state.testState.folders = [ "/etc/state" ];
        environment.etc.state.text = "hello world";
        systemd.tmpfiles.settings = {
          "ssh-key"."/root/.ssh/id_ed25519" = {
            C.argument = "${../lib/ssh/privkey}";
            z = {
              mode = "0400";
              user = "root";
            };
          };
        };
        clan.borgbackup = {
          enable = true;
          destinations.test = {
            repo = "borg@localhost:.";
            rsh = "ssh -i /root/.ssh/id_ed25519 -o StrictHostKeyChecking=no";
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
