{
  lib,
  # TODO: Get rid of self here.
  # DONT add any new functions that depend on self here.
  # If a lib function depends on a piece in clan-core add that piece to the function arguments
  self,
  ...
}:
# Produces the
# 'clanLib' attribute set
# Wrapped with fix, so we can depend on other clanLib functions without passing the whole flake
lib.fix (
  clanLib:
  let
    buildClanLib = (
      clanLib.callLib ./modules {
        clan-core = self;
      }
    );
  in
  {

    inherit (buildClanLib)
      buildClan
      clan
      ;
    /**
      Like callPackage, but doesn't try to automatically detect arguments
      'lib' and 'clanLib' are always passed, plus the additional arguments
    */
    callLib = file: args: import file ({ inherit lib clanLib; } // args);

    evalService = clanLib.callLib ./modules/inventory/distributed-service/evalService.nix { };
    # ------------------------------------
    # ClanLib functions
    evalClan = clanLib.callLib ./modules/inventory/eval-clan-modules { };
    inventory = clanLib.callLib ./modules/inventory { };
    modules = clanLib.callLib ./modules/inventory/frontmatter { };
    test = clanLib.callLib ./test { };
    # Custom types
    types = clanLib.callLib ./types { };

    # Plain imports.
    introspection = import ./introspection { inherit lib; };
    jsonschema = import ./jsonschema { inherit lib; };
    facts = import ./facts.nix { inherit lib; };

    # flakes
    flakes = clanLib.callLib ./flakes.nix { };
  }
)
