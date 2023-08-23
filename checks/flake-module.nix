{ self, ... }: {
  perSystem = { pkgs, ... }: {
    checks =
      let
        nixosTestArgs = {
          # reference to nixpkgs for the current system
          inherit pkgs;
          # this gives us a reference to our flake but also all flake inputs
          inherit self;
        };
        nixosTests = {
          # import our test
          secrets = import ./secrets nixosTestArgs;
        };
        schemaTests = pkgs.callPackages ./schemas.nix {
          inherit self;
        };
      in
      nixosTests // schemaTests;
  };
}
