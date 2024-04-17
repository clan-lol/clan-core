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
    { clanCore.clanDir = ./.; }
  ] ++ allNixosModules;

  # TODO: optimally we would not have to evaluate all nixos modules for every page
  #   but some of our module options secretly depend on nixos modules.
  #   We would have to get rid of these implicit dependencies and make them explicit
  clanCoreNixos = pkgs.nixos { imports = clanCoreNixosModules; };

  # using extendModules here instead of re-evaluating nixos every time
  #   improves eval performance slightly (10%)
  getOptions = modules: (clanCoreNixos.extendModules { inherit modules; }).options;

  evalDocs =
    options:
    pkgs.nixosOptionsDoc {
      options = options;
      warningsAreErrors = false;
    };

  # clanModules docs
  clanModulesDocs = builtins.mapAttrs (
    name: module: (evalDocs ((getOptions [ module ]).clan.${name} or { })).optionsJSON
  ) clanModules;

  clanModulesReadmes = builtins.mapAttrs (
    module_name: _module:
    let
      readme = "${self}/clanModules/${module_name}/README.md";
      readmeContents =
        if
          builtins.trace "Trying to get Module README.md for ${module_name} from ${readme}"
            # TODO: Edge cases
            (builtins.pathExists readme)
        then
          (builtins.readFile readme)
        else
          null;
    in
    readmeContents
  ) clanModules;

  # clanCore docs
  clanCoreDocs = (evalDocs (getOptions [ ]).clanCore).optionsJSON;
in
{
  inherit clanModulesReadmes;
  clanCore = clanCoreDocs;
  clanModules = clanModulesDocs;
}
