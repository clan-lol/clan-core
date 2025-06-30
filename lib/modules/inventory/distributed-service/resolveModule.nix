{ lib }:
{
  moduleSpec,
  flakeInputs,
  clanCoreModules,
}:
let
  inputError = throw ''
    Flake doesn't provide input with name '${moduleSpec.input}'

    Choose one of the following inputs:
    - ${
      builtins.concatStringsSep "\n- " (
        lib.attrNames (lib.filterAttrs (_name: input: input ? clan) flakeInputs)
      )
    }

    To import a local module from 'clan.modules' remove the 'input' attribute from the module definition
    Remove the following line from the module definition:

    ...
    - module.input = "${moduleSpec.input}"

  '';
  resolvedModuleSet =
    # If the module.name is self then take the modules defined in the flake
    # Otherwise its an external input which provides the modules via 'clan.modules' attribute
    let
      input =
        if moduleSpec.input == null then
          { clan.modules = clanCoreModules; }
        else
          flakeInputs.${moduleSpec.input} or inputError;
    in
    input.clan.modules
      or (throw "flake input '${moduleSpec.input}' doesn't export any clan services via the `clan.modules` output attribute");

  resolvedModule =
    resolvedModuleSet.${moduleSpec.name} or (throw ''
      ${
        lib.optionalString (
          moduleSpec.input != null
        ) "flake input '${moduleSpec.input}' doesn't provide clan-module with name '${moduleSpec.name}'."
      }${
        lib.optionalString (
          moduleSpec.input == null
        ) "clan-core doesn't provide clan-module with name '${moduleSpec.name}'."
      }

      Set `module.input = "self"` if the module is defined in your own flake.
      Set `module.input = "<flake-input>" if the module is defined by a flake input called `<flake-input>`.
      Unset `module.input` (or set module.input = null) - to use the clan-core module '${moduleSpec.name}'
    '');
in
resolvedModule
