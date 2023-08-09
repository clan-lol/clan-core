{ self, lib, inputs, ... }:
let
  inherit (builtins)
    mapAttrs
    toJSON
    toFile
    ;
  inherit (lib)
    mapAttrs'
    ;
  clanLib = self.lib;
  clanModules = self.clanModules;

  baseModule = {
    imports =
      (import (inputs.nixpkgs + "/nixos/modules/module-list.nix"))
      ++ [{
        nixpkgs.hostPlatform = "x86_64-linux";
      }];
  };

  optionsFromModule = module:
    let
      evaled = lib.evalModules {
        modules = [ module baseModule ];
      };
    in
    evaled.options.clan.networking;

  clanModuleSchemas = mapAttrs (_: module: clanLib.jsonschema.parseOptions (optionsFromModule module)) clanModules;

in
{
  perSystem = { pkgs, ... }:
    let
      mkTest = name: schema: pkgs.runCommand "schema-${name}" { } ''
        ${pkgs.check-jsonschema}/bin/check-jsonschema \
          --check-metaschema ${toFile "schema-${name}" (toJSON schema)}
        touch $out
      '';
    in
    {
      checks = mapAttrs'
        (name: schema: {
          name = "schema-${name}";
          value = mkTest name schema;
        })
        clanModuleSchemas;
    };
}
