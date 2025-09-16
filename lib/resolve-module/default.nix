{ lib, ... }:
/**
  Resolve a module from either the clan-core modules or from a flake input.

  The logic is as follows:
  - If the moduleSpec.input is null then the module is looked up in the clanCore
  - If the moduleSpec.input is set to a string then the module is looked up in the
    flake input with that name.
*/
{
  moduleSpec,
  flakeInputs,
  clanCoreModules,
}:
let
  inputError = throw ''
    Flake doesn't provide input with name '${moduleSpec.input}'

    Choose one of the following inputs:
    - ${builtins.concatStringsSep "\n- " (lib.attrNames (flakeInputs))}

    To import any official module from '<clan-core>' remove the 'input' attribute from the module definition
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

      Remove `module.input` (or set module.input = null) - to use a <clan-core> module'

      Set `module.input = "self"` if the module is defined in your own flake.
      Set `module.input = "<flake-input>" if the module is defined by a flake input called `<flake-input>`.
    '');
in
resolvedModule
