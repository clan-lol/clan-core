(import ../lib/container-test.nix) (
  { pkgs, ... }:
  {
    name = "secrets";

    nodes.machine =
      { self, ... }:
      {
        imports = [ self.clanModules.postgres ];
      };
    testScript = ''
      start_all()
      machine.wait_for_unit("postgres")
      machine.succeed("${pkgs.netcat}/bin/nc -z -v ::1 5432")
    '';
  }
)
