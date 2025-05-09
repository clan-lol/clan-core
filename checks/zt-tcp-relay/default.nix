(
  { pkgs, ... }:
  {
    name = "zt-tcp-relay";

    nodes.machine =
      { self, ... }:
      {
        imports = [
          self.nixosModules.clanCore
          self.clanModules.zt-tcp-relay
          {
            clan.core.settings.directory = ./.;
          }
        ];
      };
    testScript = ''
      start_all()
      machine.wait_for_unit("zt-tcp-relay.service")
      out = machine.succeed("${pkgs.netcat}/bin/nc -z -v localhost 4443")
      print(out)
    '';
  }
)
