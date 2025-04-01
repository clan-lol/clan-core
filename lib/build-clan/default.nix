## WARNING: Do not add core logic here.
## This is only a wrapper such that buildClan can be called as a function.
## Add any logic to ./module.nix
{
  lib,
  nixpkgs,
  clan-core,
}:
let
  clanResultAttributes = [
    "clanInternals"
    "nixosConfigurations"
  ];
in
{
  inherit clanResultAttributes;
  flakePartsModule = {
    imports = [
      ./interface.nix
      ./module.nix
    ];
  };
  /**
    Function that returns the same result as the correlated flake-parts module
  */
  buildClan =
    {
      ## Inputs
      self ? lib.warn "Argument: 'self' must be set when using 'buildClan'." null, # Reference to the current flake
      # allows to include machine-specific modules i.e. machines.${name} = { ... }
      # A map from arch to pkgs, if specified this nixpkgs will be only imported once for each system.
      # This improves performance, but all nipxkgs.* options will be ignored.
      # deadnix: skip
      inventory ? { },
      ## Special inputs (not passed to the module system as config)
      specialArgs ? { }, # Extra arguments to pass to nixosSystem i.e. useful to make self available # A set containing clan meta: name :: string, icon :: string, description :: string
      ##
      ...
    }@attrs:
    let
      eval = import ./function-adapter.nix {
        inherit
          lib
          nixpkgs
          clan-core
          self
          ;
        inherit specialArgs;
      };
      rest = builtins.removeAttrs attrs [ "specialArgs" ];
    in
    eval {
      imports = [
        rest
        # implementation
        ./module.nix
      ];
    };
}
