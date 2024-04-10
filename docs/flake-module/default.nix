{
  self,
  lib,
  inputs,
  ...
}:
{
  imports = [ ./zola-pages.nix ];

  perSystem =
    { pkgs, ... }:
    let

      allNixosModules = (import "${inputs.nixpkgs}/nixos/modules/module-list.nix") ++ [
        "${inputs.nixpkgs}/nixos/modules/misc/assertions.nix"
        { nixpkgs.hostPlatform = "x86_64-linux"; }
      ];

      clanCoreNixosModules = [
        self.nixosModules.clanCore
        { clanCore.clanDir = ./.; }
      ] ++ allNixosModules;

      # TODO: optimally we would not have to evaluate all nixos modules for every page
      #   but some of our module options secretly depend on nixos modules.
      #   We would have to get rid of these implicit dependencies and make them explicit
      clanCoreNixos = pkgs.nixos { imports = clanCoreNixosModules; };

      # using extendModules here instead of re-evaluating nixos every time
      #   improves eval performance slightly (10%)
      options = modules: (clanCoreNixos.extendModules { inherit modules; }).options;

      docs =
        options:
        pkgs.nixosOptionsDoc {
          options = options;
          warningsAreErrors = false;
          # transform each option so that the declaration link points to git.clan.lol
          #   and not to the /nix/store
          transformOptions =
            opt:
            opt
            // {
              declarations = lib.forEach opt.declarations (
                decl:
                if lib.hasPrefix "${self}" decl then
                  let
                    subpath = lib.removePrefix "${self}" decl;
                  in
                  {
                    url = "https://git.clan.lol/clan/clan-core/src/branch/main/" + subpath;
                    name = subpath;
                  }
                else
                  decl
              );
            };
        };

      outputsFor = name: docs: { packages."docs-md-${name}" = docs.optionsCommonMark; };

      clanModulesPages = lib.flip lib.mapAttrsToList self.clanModules (
        name: module: outputsFor "module-${name}" (docs ((options [ module ]).clan.${name} or { }))
      );
    in
    {
      imports = clanModulesPages ++ [
        # renders all clanCore options in a single page
        (outputsFor "core-options" (docs (options [ ]).clanCore))
      ];
    };
}
