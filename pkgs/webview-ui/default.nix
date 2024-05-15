{ dream2nix, config, ... }:
{
  imports = [ dream2nix.modules.dream2nix.WIP-nodejs-builder-v3 ];

  mkDerivation = {
    src = ./app;
  };

  deps =
    { nixpkgs, ... }:
    {
      inherit (nixpkgs) stdenv;
    };

  WIP-nodejs-builder-v3 = {
    packageLockFile = "${config.mkDerivation.src}/package-lock.json";
  };

  name = "@clan/webview-ui";
  version = "0.0.1";
}
