## WARNING: Do not add core logic here.
## This is only a wrapper such that buildClan can be called as a function.
## Add any logic to ./module.nix
{
  lib,
  nixpkgs,
  ...
}:
{
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
    - publicAttrs: { clan :: List Str, topLevel :: List Str } Publicly exported attribute names

    # Arguments of the second function (aka 'buildClan')
    - self: Reference to the users flake
    - inventory: An "Inventory" attribute set, see the docs, for how to construct one
    - specialArgs: Extra arguments to pass to nixosSystem i.e. useful to make self available
    - ...: Any other argument of the 'clan' submodule. See the docs for all available options

    # Returns

    Public attributes of buildClan. As specified in publicAttrs.
  */
  buildClanWith =
    {
      clan-core,
      publicAttrs ? import ./public.nix,
    }:
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
      result = eval {
        imports = [
          rest
          # implementation
          ./module.nix
        ];
      };
    in
    {
      clan = lib.genAttrs publicAttrs.clan (
        name:
        result.clanInternals.${name}
          or (throw "Output: clanInternals.${name} not found. Check: ${result.file}")
      );
    }
    // lib.filterAttrs (name: _v: builtins.elem name publicAttrs.topLevel) result;
}
