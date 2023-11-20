{ callPackage }:
let
  nix-unit-src = builtins.fetchGit {
    url = "https://github.com/adisbladis/nix-unit";
    rev = "7e2ee1c70f930b9b65b9fc33c3f3eca0dfae00d1";
  };
in
callPackage nix-unit-src { }
