{ lib }:
{
  moduleSpec,
  flakeInputs,
  localModuleSet,
}:
let
  resolvedModuleSet =
    # If the module.name is self then take the modules defined in the flake
    # Otherwise its an external input which provides the modules via 'clan.modules' attribute
    if moduleSpec.input == null then
      localModuleSet
    else
      let
        input =
          flakeInputs.${moduleSpec.input} or (throw ''
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

          '');
        clanAttrs =
          input.clan
            or (throw "It seems the flake input ${moduleSpec.input} doesn't export any clan resources");
      in
      clanAttrs.modules;

  resolvedModule =
    resolvedModuleSet.${moduleSpec.name}
      or (throw "flake doesn't provide clan-module with name ${moduleSpec.name}");
in
resolvedModule
