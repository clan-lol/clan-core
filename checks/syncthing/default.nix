{
  pkgs,
  self,
  clanLib,
  ...
}:
clanLib.test.makeTestClan {
  inherit pkgs self;
  nixosTest = (
    { lib, ... }:
    {
      name = "syncthing";

      clan = {
        directory = ./.;
        inventory = {
          machines = lib.genAttrs [
            "introducer"
            "peer1"
            "peer2"
          ] (_: { });
          services = {
            syncthing.default = {
              roles.peer.machines = [
                "peer1"
                "peer2"
              ];
              roles.introducer.machines = [ "introducer" ];
            };
          };
        };
      };

      nodes.introducer = {
        # Doesn't test zerotier!
        services.syncthing.openDefaultPorts = true;
        services.syncthing.settings.folders = {
          "Shared" = {
            enable = true;
            path = "~/Shared";
            versioning = {
              type = "trashcan";
              params = {
                cleanoutDays = "30";
              };
            };
          };
        };
        clan.syncthing.autoAcceptDevices = true;
        clan.syncthing.autoShares = [ "Shared" ];
        # For faster Tests
        systemd.timers.syncthing-auto-accept.timerConfig = {
          OnActiveSec = 1;
          OnUnitActiveSec = 1;
        };
      };
      nodes.peer1 = {
        services.syncthing.openDefaultPorts = true;
      };
      nodes.peer2 = {
        services.syncthing.openDefaultPorts = true;
      };

      testScript = ''
        start_all()
        introducer.wait_for_unit("syncthing")
        peer1.wait_for_unit("syncthing")
        peer2.wait_for_unit("syncthing")
        peer1.execute("ls -la /var/lib/syncthing")
        peer2.execute("ls -la /var/lib/syncthing")
        peer1.wait_for_file("/var/lib/syncthing/Shared")
        peer2.wait_for_file("/var/lib/syncthing/Shared")
        introducer.shutdown()
        peer1.execute("echo hello > /var/lib/syncthing/Shared/hello")
        peer2.wait_for_file("/var/lib/syncthing/Shared/hello")
        out = peer2.succeed("cat /var/lib/syncthing/Shared/hello")
        assert "hello" in out
      '';
    }
  );
}
