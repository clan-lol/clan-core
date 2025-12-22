{ ... }:

{
  perSystem =
    {
      pkgs,
      ...
    }:
    let
      zerotier-src = pkgs.fetchFromGitHub {
        owner = "zerotier";
        repo = "ZeroTierOne";
        rev = "master";
        hash = "sha256-fcGVoV0Vd8TrYDE730W9GBHcVjTXB3oGqWzJRErBBzk=";
      };
      mesh-controller = pkgs.stdenv.mkDerivation rec {
        pname = "mesh-controller";
        version = "0.1.0";
        src = ./.;

        nativeBuildInputs = [
          pkgs.cmake
          pkgs.pkg-config
          pkgs.rustPlatform.cargoSetupHook
          pkgs.cargo
          pkgs.rustc
        ];

        buildInputs = [
          pkgs.openssl
        ];

        cargoDeps = pkgs.rustPlatform.importCargoLock {
          lockFile = ./Cargo.lock;
        };

        cmakeFlags = [
          "-DSOURCE_DIR=${zerotier-src}"
        ];

        # Integration tests require sudo/live networking; disable in CI builds.
        doCheck = false;

        meta = {
          description = "Patched ZeroTier daemon built with a Rust mesh controller";
          homepage = "https://github.com/zerotier/ZeroTierOne";
          license = pkgs.lib.licenses.mpl20;
          platforms = [ "x86_64-linux" ];
        };
      };
    in
    {
      packages = {
        inherit mesh-controller;
      };
    };
}
