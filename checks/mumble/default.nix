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
    let
      common =
        { pkgs, modulesPath, ... }:
        {
          imports = [
            (modulesPath + "/../tests/common/x11.nix")
          ];

          clan.services.mumble.user = "alice";
          environment.systemPackages = [ pkgs.killall ];
        };
      machines = [
        "peer1"
        "peer2"
      ];
    in
    {
      name = "mumble";

      clan = {
        directory = ./.;
        inventory = {
          machines = lib.genAttrs machines (_: { });
          services = {
            mumble.default = {
              roles.server.machines = machines;
            };
          };
        };
      };

      enableOCR = true;

      nodes.peer1 = common;
      nodes.peer2 = common;

      testScript = ''
        start_all()

        with subtest("Waiting for x"):
          peer1.wait_for_x()
          peer2.wait_for_x()

        with subtest("Waiting for murmur"):
          peer1.wait_for_unit("murmur.service")
          peer2.wait_for_unit("murmur.service")

        with subtest("Starting Mumble"):
          # starting mumble is blocking
          peer1.execute("mumble >&2 &")
          peer2.execute("mumble >&2 &")

        with subtest("Wait for Mumble"):
          peer1.wait_for_window(r"^Mumble$")
          peer2.wait_for_window(r"^Mumble$")

        with subtest("Wait for certificate creation"):
          peer1.wait_for_window(r"^Mumble$")
          peer1.sleep(3) # mumble is slow to register handlers
          peer1.send_chars("\n")
          peer1.send_chars("\n")
          peer2.wait_for_window(r"^Mumble$")
          peer2.sleep(3) # mumble is slow to register handlers
          peer2.send_chars("\n")
          peer2.send_chars("\n")

        with subtest("Wait for server connect"):
          peer1.wait_for_window(r"^Mumble Server Connect$")
          peer2.wait_for_window(r"^Mumble Server Connect$")

        with subtest("Check validity of server certificates"):
          peer1.execute("killall .mumble-wrapped")
          peer1.sleep(1)
          peer1.execute("mumble mumble://peer2 >&2 &")
          peer1.wait_for_window(r"^Mumble$")
          peer1.sleep(3) # mumble is slow to register handlers
          peer1.send_chars("\n")
          peer1.send_chars("\n")
          peer1.wait_for_text("Connected.")

          peer2.execute("killall .mumble-wrapped")
          peer2.sleep(1)
          peer2.execute("mumble mumble://peer1 >&2 &")
          peer2.wait_for_window(r"^Mumble$")
          peer2.sleep(3) # mumble is slow to register handlers
          peer2.send_chars("\n")
          peer2.send_chars("\n")
          peer2.wait_for_text("Connected.")
      '';
    }
  );
}
