{
  self,
  ...
}:
{
  imports = [
    ./clan/flake-module.nix
  ];
  perSystem =
    {
      pkgs,
      lib,
      ...
    }:
    let
      jsonDocs = import ./eval-docs.nix {
        inherit pkgs lib;
        clan-core = self;
      };
    in
    {
      legacyPackages.clan-options = jsonDocs.optionsJSON;
    };
}
