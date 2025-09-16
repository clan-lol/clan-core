## WARNING: Do not add core logic here.
## This is only a wrapper such that 'clan' can be called as a function.
{
  lib,
  clan-core,
  ...
}:
rec {
  buildClan =
    module:
    lib.warn ''
      ==================== DEPRECATION NOTICE ====================
      Please migrate
      from: 'clan = inputs.<clan-core>.lib.buildClan'
      to  : 'clan = inputs.<clan-core>.lib.clan'
      in your flake.nix.

      Please also migrate
      from: 'inherit (clan) nixosConfigurations clanInternals; '
      to  : "
              inherit (clan.config) nixosConfigurations clanInternals;
              clan = clan.config;
            "
      in your flake.nix.

      Reason:
      - Improves consistency between flake-parts and non-flake-parts users.

      - It also allows us to use the top level attribute 'clan' to expose
        attributes that can be used for cross-clan functionality.
      ============================================================
    '' (clan module).config;

  clan =
    {
      self ? lib.warn "Argument: 'self' must be set" null, # Reference to the current flake
      ...
    }@m:
    let
      nixpkgs = self.inputs.nixpkgs or clan-core.inputs.nixpkgs;
      nix-darwin = self.inputs.nix-darwin or clan-core.inputs.nix-darwin;
    in
    lib.evalModules {
      class = "clan";
      specialArgs = {
        inherit
          self
          ;
        inherit
          nixpkgs
          nix-darwin
          ;
      };
      modules = [
        m
        clan-core.modules.clan.default
      ];
    };
}
