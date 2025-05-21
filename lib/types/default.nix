{ lib, ... }:
{
  uniqueDeferredSerializableModule = lib.fix (
    self:
    # Essentially the "raw" type, but with a custom name and check
    lib.mkOptionType {
      name = "deferredModule";
      description = "deferred module that has custom check and merge behavior";
      descriptionClass = "noun";
      # Unfortunately, tryEval doesn't catch JSON errors
      check = value: lib.seq (builtins.toJSON value) true;
      merge = lib.options.mergeUniqueOption {
        message = "------";
        merge = loc: defs: {
          imports = map (
            def: lib.setDefaultModuleLocation "${def.file}, via option ${lib.showOption loc}" def.value
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
