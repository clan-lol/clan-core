{
  bash,
  callPackage,
  git,
  lib,
  openssh,
  ...
}:
let
  writers = callPackage ../builders/script-writers.nix { };
in
writers.writePython3Bin "agit" {
  flakeIgnore = [
    "E501"
  ];
  makeWrapperArgs = [
    "--prefix"
    "PATH"
    ":"
    (lib.makeBinPath [
      bash
      git
      openssh
    ])
  ];
} ./agit.py
