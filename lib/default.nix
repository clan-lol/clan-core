{
  lib,
  ...
}:
lib.fix (
  let
    f =
      clanLib:
      {
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
        jsonschema = import ./jsonschema { inherit lib clanLib; };
        docs = import ./docs.nix { inherit lib; };

        flakes = import ./flakes.nix { inherit lib clanLib; };

        fs = {
          inherit (builtins) pathExists readDir;
        };

        # ------------------------------------
        # Public ClanLib functions
        # TODO: Hoist all functions directly into clanLib

        # getPublicValue = import ./get-public-value.nix { inherit lib; };

        test = import ./test { inherit lib clanLib; };

        # Deprecated will be removed with the next release
        vars.getPublicValue = lib.warn "'vars.getPublicValue' was renamed. Use 'getPublicValue' instead." clanLib.getPublicValue;

        # Experimental
        exports = throw "clanLib.exports has been renamed. Use the utility in clanLib directly";

        /**
          Upper-case the first character, leave the rest alone

          # Inputs

          `str`
          : Input string

          # Type

          ```
          toUpperFirst :: string -> string
          ```

          # Examples
          :::{.example}
          ## `lib.strings.toUpperFirst` usage example

          ```nix
          toUpperFirst "foo"
          => "Foo"
          hasPrefix "fooBar"
          => "FooBar"
          ```

          :::
        */
        toUpperFirst =
          str:
          lib.throwIfNot (lib.isString str)
            "toUpperFirst only accepts string values, but got ${lib.typeOf str}"
            (
              let
                firstChar = lib.substring 0 1 str;
                rest = lib.substring 1 (-1) str;
              in
              lib.addContextFrom str (lib.toUpper firstChar + rest)
            );
      }
      // (import ./vars/default.nix { inherit lib; })
      // (import ./exports/exports.nix { inherit lib clanLib; });
  in
  f
)
