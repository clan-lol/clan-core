{
  lib,
  self,
  nixpkgs,
  nix-darwin ? null,
  ...
}:
# Produces the
# 'clanLib' attribute set
# Wrapped with fix, so we can depend on other clanLib functions without passing the whole flake
lib.fix (clanLib: {
  /**
    Like callPackage, but doesn't try to automatically detect arguments
    'lib' and 'clanLib' are always passed, plus the additional arguments
  */
  callLib = file: args: import file ({ inherit lib clanLib; } // args);

  # ------------------------------------
  buildClan = clanLib.buildClanModule.buildClanWith {
    clan-core = self;
    inherit nixpkgs nix-darwin;
  };
  evalServiceSchema =
    self:
    {
      moduleSpec,
      flakeInputs ? self.inputs,
      localModuleSet ? self.clan.modules,
    }:
    let
      resolvedModule = clanLib.inventory.resolveModule {
        inherit moduleSpec flakeInputs localModuleSet;
      };
    in
    (clanLib.inventory.evalClanService {
      modules = [ resolvedModule ];
      prefix = [ ];
    }).config.result.api.schema;
  # ------------------------------------
  # ClanLib functions
  evalClan = clanLib.callLib ./inventory/eval-clan-modules { };
  buildClanModule = clanLib.callLib ./build-clan { };
  inventory = clanLib.callLib ./inventory { };
  modules = clanLib.callLib ./inventory/frontmatter { };
  test = clanLib.callLib ./test { };
  # Custom types
  types = clanLib.callLib ./types { };

  # Plain imports.
  introspection = import ./introspection { inherit lib; };
  jsonschema = import ./jsonschema { inherit lib; };
  facts = import ./facts.nix { inherit lib; };

  # flakes
  flakes = clanLib.callLib ./flakes.nix {
    clan-core = self;
  };

  # deprecated
  # remove when https://git.clan.lol/clan/clan-core/pulls/3212 is implemented
  inherit (self.inputs.nix-select.lib) select;
})
