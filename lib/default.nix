{
  lib,
  ...
}:
# Produces the
# 'clanLib' attribute set
# Wrapped with fix, so we can depend on other clanLib functions without passing the whole flake
lib.fix (
  let
    f = clanLib: {
      __unfix__ = f;
      clan = throw "lib.clan is not yet initialized. Use lib.clan exported by the clan-core flake.";
      /**
        Like callPackage, but doesn't try to automatically detect arguments
        'lib' and 'clanLib' are always passed, plus the additional arguments
      */
      callLib = file: args: import file ({ inherit lib clanLib; } // args);

      checkConfig = clanLib.callLib ./clan/checkConfig.nix { };

      evalService = clanLib.callLib ./evalService.nix { };
      # ------------------------------------
      # ClanLib functions
      inventory = clanLib.callLib ./inventory { };
      test = clanLib.callLib ./test { };
      flake-inputs = clanLib.callLib ./flake-inputs.nix { };
      # Custom types
      types = clanLib.callLib ./types { };

      # Plain imports.
      introspection = import ./introspection { inherit lib; };
      jsonschema = import ./jsonschema { inherit lib; };
      docs = import ./docs.nix { inherit lib; };

      vars = import ./vars.nix { inherit lib; };

      # flakes
      flakes = clanLib.callLib ./flakes.nix { };

      # TODO: Flatten our lib functions like this:
      resolveModule = clanLib.callLib ./resolve-module { };

      fs = {
        inherit (builtins) pathExists readDir;
      };
    };
  in
  f
)
