{
  perSystem = { self', pkgs, ... }: {
    devShells.clan-cli = pkgs.callPackage ./shell.nix {
      inherit (self'.packages) clan-cli ui-assets nix-unit;
    };
    packages = {
      clan-cli = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (self'.packages) ui-assets zerotierone;
      };
      clan-openapi = self'.packages.clan-cli.clan-openapi;
      default = self'.packages.clan-cli;

      ## Optional dependencies for clan cli, we re-expose them here to make sure they all build.
      inherit (pkgs)
        age
        bash
        bubblewrap
        git
        openssh
        rsync
        sops
        sshpass
        tor
        zbar
        ;
      # Override license so that we can build zerotierone without
      # having to re-import nixpkgs.
      zerotierone = pkgs.zerotierone.overrideAttrs (_old: { meta = { }; });
      ## End optional dependencies
    };

    checks = self'.packages.clan-cli.tests;
  };

}
