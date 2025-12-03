{
  lib,
  ...
}:
lib.fix (
  let
    f = clanLib: {
      __unfix__ = f;
      clan = throw "lib.clan is not yet initialized. Use lib.clan exported by the clan-core flake.";

      # TODO: Hide from public interface
      # TODO: Flatten our lib functions like this:
      checkConfig = import ./clan/checkConfig.nix { inherit lib; };
      evalService = import ./evalService.nix { inherit lib clanLib; };

      resolveModule = import ./resolve-module { inherit lib clanLib; };
      inventory = import ./inventory { inherit lib clanLib; };
      flake-inputs = import ./flake-inputs.nix { inherit lib clanLib; };

      types = import ./types { inherit lib clanLib; };

      introspection = import ./introspection { inherit lib; };
      jsonschema = import ./jsonschema { inherit lib; };
      docs = import ./docs.nix { inherit lib; };

      flakes = import ./flakes.nix { inherit lib clanLib; };

      fs = {
        inherit (builtins) pathExists readDir;
      };

      # ------------------------------------
      # Public ClanLib functions
      # TODO: Hoist all functions directly into clanLib
      exports = import ./exports/exports.nix { inherit lib clanLib; };
      #
      vars = import ./vars.nix { inherit lib; };
      #
      test = import ./test { inherit lib clanLib; };
    };
  in
  f
)
