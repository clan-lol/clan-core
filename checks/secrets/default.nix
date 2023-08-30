(import ../lib/test-base.nix) {
  name = "secrets";

  nodes.machine = { self, config, ... }: {
    imports = [
      (self.nixosModules.clanCore)
    ];
    environment.etc."secret".source = config.sops.secrets.foo.path;
    sops.age.keyFile = ./key.age;
    clanCore.clanDir = "${./.}";
    clanCore.machineName = "machine";
    networking.hostName = "machine";
  };
  testScript = ''
    machine.succeed("cat /etc/secret >&2")
  '';
}
