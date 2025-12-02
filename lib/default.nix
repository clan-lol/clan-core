{
  lib,
  ...
}:
lib.fix (
  let
    f = clanLib: {
      __unfix__ = f;
      clan = throw "lib.clan is not yet initialized. Use lib.clan exported by the clan-core flake.";

      checkConfig = import ./clan/checkConfig.nix { inherit lib clanLib; };

      evalService = import ./evalService.nix { inherit lib clanLib; };
      # ------------------------------------
      # ClanLib functions
      inventory = import ./inventory { inherit lib clanLib; };
      test = import ./test { inherit lib clanLib; };
      flake-inputs = import ./flake-inputs.nix { inherit lib clanLib; };
      # Custom types
      types = import ./types { inherit lib clanLib; };

      # Plain imports.
      introspection = import ./introspection { inherit lib; };
      jsonschema = import ./jsonschema { inherit lib; };
      docs = import ./docs.nix { inherit lib; };

      vars = import ./vars.nix { inherit lib; };

      # flakes
      flakes = import ./flakes.nix { inherit lib clanLib; };

      # TODO: Flatten our lib functions like this:
      resolveModule = import ./resolve-module { inherit lib clanLib; };

      # Functions to help define exports
      exports = import ./exports/exports.nix { inherit lib clanLib; };

      fs = {
        inherit (builtins) pathExists readDir;
      };
    };
  in
  f
)
