{ writeShellApplication
, curl
, nix
, gnutar
, gitMinimal
, coreutils
}:
writeShellApplication {
  name = "update-ui-assets";
  runtimeInputs = [
    curl
    nix
    gnutar
    gitMinimal
    coreutils
  ];
  text = builtins.readFile ./update-ui-assets.sh;
}
