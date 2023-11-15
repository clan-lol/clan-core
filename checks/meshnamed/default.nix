(import ../lib/container-test.nix) ({ pkgs, ... }: {
  name = "meshnamed";

  nodes.machine = { self, ... }: {
    imports = [
      self.nixosModules.clanCore
      {
        clanCore.machineName = "machine";
        clan.networking.meshnamed.networks.vpn.subnet = "fd43:7def:4b50:28d0:4e99:9347:3035:17ef/88";
        clanCore.clanDir = ./.;
      }
    ];
  };
  testScript = ''
    start_all()
    machine.wait_for_unit("meshnamed")
    out = machine.succeed("${pkgs.dnsutils}/bin/dig AAAA foo.7vbx332lkaunatuzsndtanix54.vpn @meshnamed +short")
    print(out)
    assert out.strip() == "fd43:7def:4b50:28d0:4e99:9347:3035:17ef"
  '';
})
