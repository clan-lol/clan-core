{
  description = "A declarative controller for self-hosting zerotier";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      { lib, ... }:
      {
        systems = lib.systems.flakeExposed;
        perSystem =
          { pkgs, lib, ... }:
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
              default = mesh-controller;
              inherit mesh-controller;
            };

            devShells.default = pkgs.mkShell {
              packages = [
                pkgs.bashInteractive
                pkgs.cmake
                pkgs.rustc
                pkgs.cargo
              ];
              CMAKE_FLAGS = "-DSOURCE_DIR=${zerotier-src}";
            };

            checks = lib.optionalAttrs pkgs.stdenv.isLinux {
              mesh-controller-nixos-test = import ./nixos/tests/mesh-controller.nix {
                inherit pkgs zerotier-src;
              };
            };
          };
      }
    );
}
