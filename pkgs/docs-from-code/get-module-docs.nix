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

  nixosConfigurationWithClan =
    let
      evaled = lib.evalModules {
        class = "nixos";
        modules = [
          # Basemodule
          (
            { config, ... }:
            {
              imports = (import (pkgs.path + "/nixos/modules/module-list.nix"));
              nixpkgs.pkgs = pkgs;
              clan.core.name = "dummy";
              system.stateVersion = config.system.nixos.release;
              # Set this to work around a bug where `clan.core.settings.machine.name`
              # is forced due to `networking.interfaces` being forced
              # somewhere in the nixpkgs options
              facter.detected.dhcp.enable = lib.mkForce false;
            }
          )
          {
            clan.core.settings.directory = clan-core;
          }
          clan-core.nixosModules.clanCore
        ];
      };
    in
    evaled;
in
{
  # Test with:
  # nix build .\#legacyPackages.x86_64-linux.clanModulesViaService
  clanModulesViaService = lib.mapAttrs (
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
            if lib.strings.hasPrefix "_" transformed.name then
              transformed // { visible = false; }
            else
              transformed;
          options = (lib.evalModules { modules = [ role.interface ]; }).options;
          warningsAreErrors = true;
        }).optionsJSON
      ) evaluatedService.config.roles;
      manifest = evaluatedService.config.manifest;
    }
  ) clan-core.clan.modules;

  clanCore =
    (nixosOptionsDoc {
      options = nixosConfigurationWithClan.options.clan.core;
      warningsAreErrors = true;
      inherit transformOptions;
    }).optionsJSON;
}
