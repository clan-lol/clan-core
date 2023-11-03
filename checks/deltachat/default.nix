(import ../lib/container-test.nix) ({ pkgs, ... }: {
  name = "secrets";

  nodes.machine = { self, ... }: {
    imports = [
      ../../clanModules/deltachat.nix
      self.nixosModules.clanCore
      {
        clanCore.machineName = "machine";
        clanCore.clanDir = ./.;
      }
    ];
  };
  testScript = ''
    start_all()
    machine.wait_for_unit("maddy")
    # imap
    machine.succeed("${pkgs.netcat}/bin/nc -z -v ::1 143")
    # smtp submission
    machine.succeed("${pkgs.netcat}/bin/nc -z -v ::1 587")
    # smtp
    machine.succeed("${pkgs.netcat}/bin/nc -z -v ::1 25")
  '';
})
