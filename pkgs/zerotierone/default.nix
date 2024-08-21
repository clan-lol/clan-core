{
  callPackage,
  zerotierone,
  fetchFromGitHub,
  lib,
  stdenv,
}:
let
  importCargoLock = callPackage ./import-cargo-lock.nix { };
in
zerotierone.overrideAttrs (old: {
  name = "zerotierone-1.14.0-unstable-2024-07-31";
  src = fetchFromGitHub {
    owner = "zerotier";
    repo = "ZeroTierOne";
    rev = "f176e2539e10e8c0f61eb1d2e1f0e690a267a646";
    hash = "sha256-pGozwaBy9eMA8izYtGhhmJeHzGjHFLID7WC01977XxQ=";
  };
  cargoDeps = importCargoLock {
    lockFile = ./Cargo.lock;
    outputHashes = {
      "jwt-0.16.0" = "sha256-P5aJnNlcLe9sBtXZzfqHdRvxNfm6DPBcfcKOVeLZxcM=";
      "rustfsm-0.1.0" = "sha256-AYMk31QuwB1R/yr1wNl9MSWL52ERJMtkR4aSPf2waWs=";
    };
  };
  patches = [ ];
  postPatch = "cp ${./Cargo.lock} Cargo.lock";

  preBuild =
    if stdenv.isDarwin then
      ''
        makeFlagsArray+=("ARCH_FLAGS=") # disable multi-arch build
        if ! grep -q MACOS_VERSION_MIN=10.13 make-mac.mk; then
          echo "You may need to update MACOSX_DEPLOYMENT_TARGET to match the value in make-mac.mk"
          exit 1
        fi
        (cd rustybits && MACOSX_DEPLOYMENT_TARGET=10.13 cargo build -p zeroidc --release)

        cp \
          ./rustybits/target/${stdenv.hostPlatform.rust.rustcTarget}/release/libzeroidc.a \
          ./rustybits/target

        # zerotier uses the "FORCE" target as a phony target to force rebuilds.
        # We don't want to rebuild libzeroidc.a as we build want to build this library ourself for a single architecture
        touch FORCE
      ''
    else
      old.preBuild;
  meta = old.meta // {
    # halalify zerotierone
    license = lib.licenses.apsl20;
  };
})
