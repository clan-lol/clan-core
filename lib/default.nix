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

  buildClan = clanLib.buildClanModule.buildClanWith {
    clan-core = self;
    inherit nixpkgs nix-darwin;
  };
  # ------------------------------------
  # ClanLib functions
  evalClan = clanLib.callLib ./inventory/eval-clan-modules { };
  buildClanModule = clanLib.callLib ./build-clan { };
  inventory = clanLib.callLib ./inventory { };
  modules = clanLib.callLib ./inventory/frontmatter { };
  test = clanLib.callLib ./test { };

  # Plain imports.
  introspection = import ./introspection { inherit lib; };
  jsonschema = import ./jsonschema { inherit lib; };
  facts = import ./facts.nix { inherit lib; };

  # Passthrough from self.inputs
  # TODO: Can we make these agnostic from the name of the input?
  inherit (self.inputs.nix-select.lib) parseSelector applySelectors select;
})
