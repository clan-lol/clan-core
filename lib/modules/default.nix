## WARNING: Do not add core logic here.
## This is only a wrapper such that buildClan can be called as a function.
## Add any logic to ./module.nix
{
  lib,
  clanLib,
  clan-core,
  nixpkgs,
  nix-darwin,
}:
rec {
  # ------------------------------------
  buildClan = buildClanWith {
    inherit
      clan-core
      nixpkgs
      nix-darwin
      ;
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
      # TODO: Below should be module options such that the user can override them?
      nixpkgs,
      nix-darwin ? null,
    }:
    {
      ## Inputs
      self ? lib.warn "Argument: 'self' must be set when using 'buildClan'." null, # Reference to the current flake
      specialArgs ? { }, # Extra arguments to pass to nixosSystem i.e. useful to make self available
      ...
    }@m:
    let
      result = lib.evalModules {
        specialArgs = {
          inherit (clan-core) clanLib;
          inherit
            self
            clan-core
            nixpkgs
            nix-darwin
            ;
        };
        modules = [
          # buildClan arguments are equivalent to specifying a module
          m
          clanLib.module
        ];
      };
    in
    # Remove result.config in 26. July
    result
    // (lib.mapAttrs (
      n: v: lib.warn "buildClan output: Use 'config.${n}' instead of '${n}'" v
    ) result.config);
}
