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

  pushPositions = map (
    def:
    lib.mapAttrs (_n: v: {
      inherit (def) file;
      value = v;
    }) def.value
  );

  unwrapNullOr =
    type:
    let
      typeName = type.name or null;
    in
    if typeName == "nullOr" then type.nestedTypes.name or null else typeName;

  mergeAttrs =
    { type, definitionsWithLocations }:
    let
      # Vendored merge from lib.types.attrsOf
      # Because we still cannot access highest prio for the individual attrs yet.
      elemType = type.nestedTypes.elemType;
      mergedAttrs = lib.zipAttrsWith (name: defs: lib.modules.mergeDefinitions ([ name ]) elemType defs) (
        pushPositions definitionsWithLocations
      );
      headType = unwrapNullOr elemType;
      nullable = elemType.name or null == "nullOr";
      total = elemType.name or null == "submodule";
    in
    lib.mapAttrs (_name: merged: {
      __this = {
        prio = merged.defsFinal'.highestPrio;
        files = map (def: def.file) merged.defsFinal'.values;
        inherit
          headType
          nullable
          total
          ;
      };
    }) mergedAttrs;

  /**
    Takes a set of options as returned by `configuration`

    Returns a recursive structure that contains '__this' along with attribute names that map to the same structure.

    Within the reserved attribute '__this' the following attributes are available:

    - prio: The highest priority this option was defined with
    - files: A list of files this option was defined in
    - type: The type of this option (e.g. "string", "attrsOf
    - total: Whether this is a total object. Meaning all attributes are fixed. No additional attributes can be added. Or one of them removed.

    Example Result:
    {
      foo = {
        __this = { ... };
        bar = {
          __this = { ... };
        };
        baz = {
          __this = { ... };
        };
      };
    }
  */
  getPrios =
    {
      options,
    }:
    let
      filteredOptions = filterOptions options;
    in
    lib.mapAttrs (
      _: opt:
      let
        headType = unwrapNullOr opt.type;
        nullable = opt.type.name or null == "nullOr";
        total = opt.type.name or null == "submodule";

        definitionInfo = {
          __this = {
            prio = opt.highestPrio or null;
            files = opt.files or [ ];
            inherit headType nullable total;
          };
        };

        # TODO: respect freeformType
        submodulePrios = getPrios {
          options =
            filterOptions
              opt.valueMeta.configuration.options or (throw "Please use a newer nixpkgs version >=25.11");
        };

        /**
          Maps attrsOf and lazyAttrsOf
        */
        handleAttrsOf =
          type: defs: attrs:
          lib.mapAttrs (
            name: meta:
            (mergeAttrs {
              inherit type;
              definitionsWithLocations = defs;
            }).${name}
            // handleMeta {
              inherit meta;
              definitionsWithLocations =
                (builtins.zipAttrsWith (_name: values: values) (pushPositions defs)).${name};
            }
          ) attrs;

        /**
          Maps attrsOf and lazyAttrsOf
        */
        handleListOf = list: { __list = lib.map handleMeta { meta = list; }; };

        /**
          Unwraps the valueMeta of an option based on its type
        */
        handleMeta =
          {
            meta,
            definitionsWithLocations ? [ ],
          }:
          let
            hasType = meta ? _internal.type;
            type = meta._internal.type;
          in
          if !hasType then
            { }
          else if type.name == "submodule" then
            # TODO: handle types
            getPrios { options = filterOptions meta.configuration.options; }
          else if type.name == "attrsOf" || type.name == "lazyAttrsOf" then
            handleAttrsOf meta._internal.type definitionsWithLocations meta.attrs
          # TODO: Add index support in nixpkgs first
          # else if type.name == "listOf" then
          #   handleListOf meta.list
          else
            throw "Yet Unsupported type: ${type.name}";
      in
      if opt ? type && opt.type.name == "submodule" then
        (definitionInfo) // submodulePrios
      else if opt ? type && (opt.type.name == "attrsOf" || opt.type.name == "lazyAttrsOf") then
        definitionInfo // (handleAttrsOf opt.type opt.definitionsWithLocations opt.valueMeta.attrs)
      # TODO: Add index support in nixpkgs, otherwise we cannot
      else if opt ? type && (opt.type.name == "listOf") then
        definitionInfo // (handleListOf opt.valueMeta.list)
      else if opt ? type && opt._type == "option" then
        definitionInfo
      else
        getPrios { options = opt; }
    ) filteredOptions;
in
{
  inherit getPrios;
}
