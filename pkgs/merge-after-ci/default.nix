{
  bash,
  callPackage,
  coreutils,
  git,
  lib,
  nix,
  openssh,
  tea,
  tea-create-pr,
  ...
}:
let
  writers = callPackage ../builders/script-writers.nix { };
in
writers.writePython3Bin "merge-after-ci" {
  makeWrapperArgs = [
    "--prefix"
    "PATH"
    ":"
    (lib.makeBinPath [
      bash
      coreutils
      git
      nix
      openssh
      tea
      tea-create-pr
    ])
  ];
} ./merge-after-ci.py
