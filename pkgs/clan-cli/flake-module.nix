{ self, ... }: {
  perSystem = { self', pkgs, ... }: {
    devShells.clan-cli = pkgs.callPackage ./shell.nix {
      inherit self;
      inherit (self'.packages) clan-cli;
    };
    packages = {
      clan-cli = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit self;
        zerotierone = self'.packages.zerotierone;
      };
      clan-openapi = self'.packages.clan-cli.clan-openapi;
      default = self'.packages.clan-cli;

      ## Optional dependencies for clan cli, we re-expose them here to make sure they all build.
      inherit (pkgs)
        bash
        bubblewrap
        openssh
        sshpass
        zbar
        tor
        age
        rsync
        sops;
      # Override license so that we can build zerotierone without
      # having to re-import nixpkgs.
      zerotierone = pkgs.zerotierone.overrideAttrs (_old: { meta = { }; });
      ## End optional dependencies
    };

    checks = self'.packages.clan-cli.tests;
  };

}
