{
  pkgs,
  self,
  clanLib,
  ...
}:
clanLib.test.makeTestClan {
  inherit pkgs self;
  # TODO: container driver does not support: sleep, wait_for_window, send_chars, wait_for_text
  useContainers = false;
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
        import time
        import re


        def machine_has_text(machine: Machine, regex: str) -> bool:
            variants = machine.get_screen_text_variants()
            # for debugging
            # machine.screenshot(f"/tmp/{machine.name}.png")
            for text in variants:
                print(f"Expecting '{regex}' in '{text}'")
                if re.search(regex, text) is not None:
                    return True
            return False

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
          peer1.wait_for_window(r"Mumble")
          peer2.wait_for_window(r"Mumble")

        with subtest("Wait for certificate creation"):
          peer1.wait_for_window(r"Mumble")
          peer2.wait_for_window(r"Mumble")

          for i in range(20):
            time.sleep(1)
            peer1.send_chars("\n")
            peer1.send_chars("\n")
            peer2.send_chars("\n")
            peer2.send_chars("\n")
            if machine_has_text(peer1, r"Mumble Server Connect") and \
               machine_has_text(peer2, r"Mumble Server Connect"):
              break
          else:
            raise Exception("Timeout waiting for certificate creation")

        with subtest("Check validity of server certificates"):
          peer1.execute("killall .mumble-wrapped")
          peer1.sleep(1)
          peer1.execute("mumble mumble://peer2 >&2 &")
          peer1.wait_for_window(r"Mumble")

          for i in range(20):
            time.sleep(1)
            peer1.send_chars("\n")
            peer1.send_chars("\n")
            if machine_has_text(peer1, "Connected."):
              break
          else:
            raise Exception("Timeout waiting for certificate creation")

          peer2.execute("killall .mumble-wrapped")
          peer2.sleep(1)
          peer2.execute("mumble mumble://peer1 >&2 &")
          peer2.wait_for_window(r"Mumble")

          for i in range(20):
            time.sleep(1)
            peer2.send_chars("\n")
            peer2.send_chars("\n")
            if machine_has_text(peer2, "Connected."):
              break
          else:
            raise Exception("Timeout waiting for certificate creation")
      '';
    }
  );
}
