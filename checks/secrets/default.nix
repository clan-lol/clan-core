(import ../lib/test-base.nix) {
  name = "secrets";

  nodes.machine = { self, config, ... }: {
    imports = [
      self.nixosModules.secrets
    ];
    environment.etc."secret".source = config.sops.secrets.foo.path;
    sops.age.keyFile = ./key.age;
    clan.sops.sopsDirectory = ./sops;
    networking.hostName = "machine";
  };
  testScript = ''
    machine.succeed("cat /etc/secret >&2")
  '';
}
