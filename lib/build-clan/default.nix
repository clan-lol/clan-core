## WARNING: Do not add core logic here.
## This is only a wrapper such that buildClan can be called as a function.
## Add any logic to ./module.nix
{
  lib,
  nixpkgs,
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
    A function that takes some arguments such as 'clan-core' and returns the 'buildClan' function.

    # Arguments of the first function
    - clan-core: Self, provided by our flake-parts module

    # Arguments of the second function (aka 'buildClan')
    - self: Reference to the users flake
    - inventory: An "Inventory" attribute set, see the docs, for how to construct one
    - specialArgs: Extra arguments to pass to nixosSystem i.e. useful to make self available
    - ...: Any other argument of the 'clan' submodule. See the docs for all available options

    # Returns

    A module evaluation containing '.config' and '.options'

    NOTE:
    The result might export all kinds of options at the '.config' top level.
  */
  buildClanWith =
    { clan-core }:
    {
      ## Inputs
      self ? lib.warn "Argument: 'self' must be set when using 'buildClan'." null, # Reference to the current flake
      # allows to include machine-specific modules i.e. machines.${name} = { ... }
      # A map from arch to pkgs, if specified this nixpkgs will be only imported once for each system.
      # This improves performance, but all nipxkgs.* options will be ignored.
      # deadnix: skip
      inventory ? { },
      ## Special inputs (not passed to the module system as config)
      specialArgs ? { }, # Extra arguments to pass to nixosSystem i.e. useful to make self available
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
