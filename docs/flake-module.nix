{
  self,
  lib,
  inputs,
  ...
}:
{
  perSystem =
    { pkgs, ... }:
    let

      allNixosModules = (import "${inputs.nixpkgs}/nixos/modules/module-list.nix") ++ [
        "${inputs.nixpkgs}/nixos/modules/misc/assertions.nix"
        { nixpkgs.hostPlatform = "x86_64-linux"; }
      ];

      clanCoreNixosModules = [ self.nixosModules.clanCore ] ++ allNixosModules;

      # options = modules: (inputs.nixpkgs.legacyPackages.x86_64-linux.nixos { imports = modules; }).options;
      options =
        modules:
        (lib.evalModules {
          modules = modules;
          # modules = modules ++ ["${inputs.nixpkgs}/nixos/modules/misc/assertions.nix"];
          # specialArgs = { pkgs = pkgs; };
        }).options;

      docs =
        options:
        pkgs.nixosOptionsDoc {
          options = options;
          warningsAreErrors = false;
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
        name: module:
        outputsFor "module-${name}" (
          docs (options ([ module ] ++ clanCoreNixosModules)).clan.${name} or { }
        )
      );
    in
    {
      imports =
        clanModulesPages
        # uncomment to render clanCore top-level options as extra pages
        # ++ clanCorePages
        ++ [
          # renders all clanCore options as a single page
          (outputsFor "core-options" (docs (options clanCoreNixosModules).clanCore))
        ];
    };
}
