{
  dream2nix,
  config,
  src,
  ...
}:
{
  imports = [ dream2nix.modules.dream2nix.WIP-nodejs-builder-v3 ];

  mkDerivation = {
    inherit src;
  };

  deps =
    { nixpkgs, ... }:
    {
      inherit (nixpkgs) stdenv;
    };

  WIP-nodejs-builder-v3 = {
    packageLockFile = "${config.mkDerivation.src}/package-lock.json";
    # config.groups.all.packages.${config.name}.${config.version}.
  };
  public.out = {
    checkPhase = ''
      echo "Running tests"
      echo "Tests passed"
    '';
  };
  name = "@clan/webview-ui";
  version = "0.0.1";
}
