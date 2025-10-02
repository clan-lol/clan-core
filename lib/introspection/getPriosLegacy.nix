{
  lib ? import <nixpkgs/lib>,
}:
let
  filterOptions = lib.filterAttrs (
    name: _:
    !builtins.elem name [
      "_module"
      "_freeformOptions"
    ]
  );

  # Use for nixpkgs < 25.11
  getPriosLegacy =
    {
      options,
    }:
    let
      filteredOptions = filterOptions options;
    in
    lib.mapAttrs (
      _: opt:
      let
        prio = {
          __prio = opt.highestPrio;
        };
        filteredSubOptions = filterOptions (opt.type.getSubOptions opt.loc);

        zipDefs = builtins.zipAttrsWith (_: vs: vs);

        prioPerValue =
          { type, defs }:
          lib.mapAttrs (
            attrName: prioSet:
            let
              # Evaluate the submodule
              # Remove once: https://github.com/NixOS/nixpkgs/pull/391544 lands
              # This is currently a workaround to get the submodule options
              # It also has a certain loss of information, on nested attrsOf, which is rare, but not ideal.
              options = filteredSubOptions;
              modules = (
                [
                  {
                    inherit options;
                    _file = "<artifical submodule>";
                  }
                ]
                ++ map (config: { inherit config; }) defs.${attrName}
              );
              submoduleEval = lib.evalModules {
                inherit modules;
              };
            in
            (lib.optionalAttrs (prioSet ? highestPrio) {
              __prio = prioSet.highestPrio;
            })
            // (
              if type.nestedTypes.elemType.name == "submodule" then
                getPriosLegacy { options = submoduleEval.options; }
              else
                # Nested attrsOf
                (lib.optionalAttrs
                  (type.nestedTypes.elemType.name == "attrsOf" || type.nestedTypes.elemType.name == "lazyAttrsOf")
                  (
                    prioPerValue {
                      type = type.nestedTypes.elemType;
                      defs = zipDefs defs.${attrName};
                    } prioSet.value
                  )
                )
            )
          );

        submodulePrios =
          let
            modules = (opt.definitions ++ opt.type.getSubModules);
            submoduleEval = lib.evalModules {
              inherit modules;
            };
          in
          getPriosLegacy { options = filterOptions submoduleEval.options; };

      in
      if opt ? type && opt.type.name == "submodule" then
        (prio) // submodulePrios
      else if opt ? type && (opt.type.name == "attrsOf" || opt.type.name == "lazyAttrsOf") then
        prio
        // (prioPerValue {
          type = opt.type;
          defs = zipDefs opt.definitions;
        } (lib.modules.mergeAttrDefinitionsWithPrio opt))
      else if opt ? type && opt._type == "option" then
        prio
      else
        getPriosLegacy { options = opt; }
    ) filteredOptions;
in
getPriosLegacy
