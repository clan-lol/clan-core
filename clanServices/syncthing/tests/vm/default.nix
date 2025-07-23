{
  name = "service-syncthing-service";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {
      machines.machine1 = { };
      machines.machine2 = { };
      machines.machine3 = { };
      machines.machine4 = { };

      instances.default = {
        module.name = "syncthing-service";
        module.input = "self";
        roles.peer.tags.all = { };
        roles.peer.settings.folders = {
          documents = {
            path = "/var/lib/syncthing/documents";
            type = "sendreceive";
            rescanIntervalS = 1;
          };
          partly_shared = {
            devices = [
              "machine1"
              "machine4"
            ];
            path = "~/music";
            type = "sendreceive";
          };
        };

      };
      instances.small = {
        module.name = "syncthing-service";
        module.input = "self";
        roles.peer.machines = {
          machine3 = { };
          machine4 = { };
        };
        roles.peer.settings.folders = {
          pictures = {
            path = "~/pictures";
            type = "sendreceive";
          };
        };
      };
    };
  };

  testScript =
    { ... }:
    ''
      start_all()

      machine1.wait_for_unit("syncthing.service")
      machine2.wait_for_unit("syncthing.service")
      machine3.wait_for_unit("syncthing.service")
      machine4.wait_for_unit("syncthing.service")

      machine1.wait_for_open_port(8384)
      machine2.wait_for_open_port(8384)
      machine3.wait_for_open_port(8384)
      machine4.wait_for_open_port(8384)

      machine1.wait_for_open_port(22000)
      machine2.wait_for_open_port(22000)
      machine3.wait_for_open_port(22000)
      machine4.wait_for_open_port(22000)

      # Check that the correct folders are synchronized
      # documents - all
      machine1.wait_for_file("/var/lib/syncthing/documents")
      machine2.wait_for_file("/var/lib/syncthing/documents")
      machine3.wait_for_file("/var/lib/syncthing/documents")
      machine4.wait_for_file("/var/lib/syncthing/documents")
      # music - machine 1 & 4
      machine1.wait_for_file("/var/lib/syncthing/music")
      machine4.wait_for_file("/var/lib/syncthing/music")
      # pictures - machine 3 & 4
      machine3.wait_for_file("/var/lib/syncthing/pictures")
      machine4.wait_for_file("/var/lib/syncthing/pictures")

      machine1.succeed("echo document > /var/lib/syncthing/documents/document")
      machine1.succeed("echo music > /var/lib/syncthing/music/music")
      machine3.succeed("echo picture > /var/lib/syncthing/pictures/picture")

      machine2.wait_for_file("/var/lib/syncthing/documents/document")
      machine3.wait_for_file("/var/lib/syncthing/documents/document")
      machine4.wait_for_file("/var/lib/syncthing/documents/document")

      machine4.wait_for_file("/var/lib/syncthing/music/music")

      machine4.wait_for_file("/var/lib/syncthing/pictures/picture")
    '';
}
