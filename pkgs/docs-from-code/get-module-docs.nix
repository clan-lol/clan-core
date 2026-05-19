{
  nixosOptionsDoc,
  lib,
  pkgs,
  clan-core,
  ...
}:
let
  inherit (clan-core.clanLib.docs) stripStorePathsFromDeclarations;
  transformOptions = stripStorePathsFromDeclarations;

  clanEval = clan-core.clanLib.clan {
    # name = "jon's clan";
    self = { };
    directory = ./.;
    machines.jon =
      { config, ... }:
      {
        nixpkgs.pkgs = pkgs;
        system.stateVersion = config.system.nixos.release;
      };
  };

  nixosConfigurationWithClan = clanEval.config.nixosConfigurations.jon;
in
{
  inherit clanEval;
  # Test with:
  # nix build .\#legacyPackages.x86_64-linux.clanModulesViaService
  clanModulesViaService =
    let
      deprecated = clan-core.clan.deprecatedModules or [ ];
      activeModules = lib.filterAttrs (name: _: !(lib.elem name deprecated)) clan-core.clan.modules;
    in
    lib.mapAttrs (
      _moduleName: moduleValue:
      let
        evaluatedService = clan-core.clanLib.evalService {
          modules = [ moduleValue ];
          prefix = [ ];
        };
      in
      {
        roles = lib.mapAttrs (
          _roleName: role:
          (nixosOptionsDoc {
            transformOptions =
              opt:
              let
                # Apply store path stripping first
                transformed = transformOptions opt;
              in
              if lib.hasPrefix "_" transformed.name then transformed // { visible = false; } else transformed;
            options = (lib.evalModules { modules = [ role.interface ]; }).options;
            warningsAreErrors = true;
          }).optionsJSON
        ) evaluatedService.config.roles;
        manifest = evaluatedService.config.manifest;
      }
    ) activeModules;

  clanCore =
    (nixosOptionsDoc {
      options = nixosConfigurationWithClan.options.clan.core;
      warningsAreErrors = true;
      inherit transformOptions;
    }).optionsJSON;
}
