{ lib, ... }:
{
  uniqueDeferredSerializableModule = lib.fix (
    self:

    let
      checkDef = loc: def: if def.value ? imports then throw "uniqueDeferredSerializableModule doesn't allow nested imports" else def;
    in
    # Essentially the "raw" type, but with a custom name and check
    lib.mkOptionType {
      name = "deferredModule";
      description = "deferred custom module. Must be JSON serializable.";
      descriptionClass = "noun";
      # Unfortunately, tryEval doesn't catch JSON errors
      check = value: lib.seq (builtins.toJSON value) (lib.isAttrs value);
      merge = lib.options.mergeUniqueOption {
        message = "------";
        merge = loc: defs: {
          imports = map (
            def:
            lib.seq (checkDef loc def)
            lib.setDefaultModuleLocation "${def.file}, via option ${lib.showOption loc}" def.value
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
}
