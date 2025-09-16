{
  lib,
  # TODO: Get rid of self here.
  # DONT add any new functions that depend on self here.
  # If a lib function depends on a piece in clan-core add that piece to the function arguments
  self ? throw "'self' should not be used in lib/default.nix, dont depend on it. It will be removed in short notice.",
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
    inventory = clanLib.callLib ./modules/inventory { };
    test = clanLib.callLib ./test { };
    flake-inputs = clanLib.callLib ./flake-inputs.nix { };
    # Custom types
    types = clanLib.callLib ./types { };

    # Plain imports.
    introspection = import ./introspection { inherit lib; };
    jsonschema = import ./jsonschema { inherit lib; };
    facts = import ./facts.nix { inherit lib; };
    docs = import ./docs.nix { inherit lib; };

    # flakes
    flakes = clanLib.callLib ./flakes.nix { };

    # TODO: Flatten our lib functions like this:
    resolveModule = clanLib.callLib ./resolve-module { };
  }
)
