{ lib, ... }:
let
  inherit (lib)
    fix
    mkOptionType
    seq
    isAttrs
    setDefaultModuleLocation
    showOption
    isFunction
    warnIf
    length
    ;
  inherit (lib.options) mergeUniqueOption;
  inherit (lib.types) submoduleWith path;
in
{
  /**
    A custom type for deferred modules that guarantee to be JSON serializable.

    This type guarantees that the module is serializable by checking all definitions.
    Nix doesn't allow to raise a nice error if the module is not serializable.

    It applies the following restrictions:

    - Enforces that there is only one definition.
    - Enforces that the definition is JSON serializable
    - Disallows nested imports
  */
  uniqueDeferredSerializableModule = fix (
    self:
    let
      checkDef =
        _loc: def:
        if def.value ? imports then
          throw "uniqueDeferredSerializableModule doesn't allow nested imports"
        else
          def;
    in
    # Essentially the "raw" type, but with a custom name and check
    mkOptionType {
      name = "deferredModule";
      description = "deferred custom module. Must be JSON serializable.";
      descriptionClass = "noun";
      # Unfortunately, tryEval doesn't catch JSON errors
      check = value: seq (builtins.toJSON value) (isAttrs value);
      merge = mergeUniqueOption {
        message = "------";
        merge = loc: defs: {
          imports = map (
            def:
            seq (checkDef loc def) setDefaultModuleLocation "${def.file}, via option ${showOption loc}"
              def.value
          ) defs;
        };
      };
      functor = {
        inherit (self) name;
        type = self;
        # Non mergable type
        binOp = _a: _b: null;
      };
    }
  );

  /**
    Custom extension of deferredModuleWith

    If defined in two places (i.e. once in clan-core, once in the user flake)
    it prints the given warning

    If its exlusively set, then it remains silent

    Mimics the behavior of "readOnly" in a soft way
  */
  exclusiveDeferredModule = fix (
    self:
    attrs@{
      staticModules ? [ ],
      warning,
    }:
    mkOptionType {
      name = "deferredModuleWith";
      description = "module";
      descriptionClass = "noun";
      check = x: isAttrs x || isFunction x || path.check x;
      merge =
        loc: defs:
        let
          warnDefs = warnIf (length defs > 1) warning;
        in
        {
          imports =
            staticModules
            ++ map (def: setDefaultModuleLocation "${def.file}, via option ${showOption loc}" def.value) (
              warnDefs defs
            );
        };
      inherit (submoduleWith { modules = staticModules; })
        getSubOptions
        getSubModules
        ;
      substSubModules =
        m:
        self (
          attrs
          // {
            staticModules = m;
          }
        );
    }
  );
}
