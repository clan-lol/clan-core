{ self, ... }: {
  perSystem = { self', pkgs, ... }: {
    devShells.clan = pkgs.callPackage ./shell.nix {
      inherit self;
      inherit (self'.packages) clan;
    };
    packages = {
      clan = pkgs.callPackage ./default.nix {
        inherit self;
        zerotierone = self'.packages.zerotierone;
      };
      default = self'.packages.clan;

      ## Optional dependencies for clan cli, we re-expose them here to make sure they all build.
      inherit (pkgs)
        bash
        bubblewrap
        openssh
        sshpass
        zbar
        tor
        sops
        age;
      # Override license so that we can build zerotierone without 
      # having to re-import nixpkgs.
      zerotierone = pkgs.zerotierone.overrideAttrs (_old: { meta = { }; });
      ## End optional dependencies
    };
    checks = self'.packages.clan.tests;
  };
}
