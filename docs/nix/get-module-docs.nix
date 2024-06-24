{
  nixpkgs,
  pkgs,
  clanCore,
  clanModules,
  self,
}:
let
  allNixosModules = (import "${nixpkgs}/nixos/modules/module-list.nix") ++ [
    "${nixpkgs}/nixos/modules/misc/assertions.nix"
    { nixpkgs.hostPlatform = "x86_64-linux"; }
  ];

  clanCoreNixosModules = [
    clanCore
    { clan.core.clanDir = ./.; }
  ] ++ allNixosModules;

  # TODO: optimally we would not have to evaluate all nixos modules for every page
  #   but some of our module options secretly depend on nixos modules.
  #   We would have to get rid of these implicit dependencies and make them explicit
  clanCoreNixos = pkgs.nixos { imports = clanCoreNixosModules; };

  # using extendModules here instead of re-evaluating nixos every time
  #   improves eval performance slightly (10%)
  getOptions = modules: (clanCoreNixos.extendModules { inherit modules; }).options;

  getOptionsWithoutCore = modules: builtins.removeAttrs (getOptions modules) [ "core" ];

  evalDocs =
    options:
    pkgs.nixosOptionsDoc {
      options = options;
      warningsAreErrors = false;
    };

  # clanModules docs
  clanModulesDocs = builtins.mapAttrs (
    name: module: (evalDocs ((getOptionsWithoutCore [ module ]).clan.${name} or { })).optionsJSON
  ) clanModules;

  clanModulesReadmes = builtins.mapAttrs (
    module_name: _module: self.lib.modules.getReadme module_name
  ) clanModules;

  clanModulesMeta = builtins.mapAttrs (
    module_name: _module:
    (self.lib.evalClanModules [ module_name ]).config.clan.${module_name}.meta or { }
  ) clanModules;

  # clanCore docs
  clanCoreDocs = (evalDocs (getOptions [ ]).clan.core).optionsJSON;
in
{
  inherit clanModulesReadmes clanModulesMeta;
  clanCore = clanCoreDocs;
  clanModules = clanModulesDocs;
}
