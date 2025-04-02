{ lib, clanLib }:
{
  inherit (import ./build-inventory { inherit lib clanLib; }) buildInventory;
  interface = ./build-inventory/interface.nix;
  mapInstances = clanLib.callLib ./distributed-service/inventory-adapter.nix { };
  # Returns the list of machine names
  # { ... } -> [ string ]
  resolveTags =
    {
      # Available InventoryMachines :: { {name} :: { tags = [ string ]; }; }
      machines,
      # Requested members :: { machines, tags }
      # Those will be resolved against the available machines
      members,
      # Not needed for resolution - only for error reporting
      roleName,
      instanceName,
    }:
    {
      machines =
        members.machines or [ ]
        ++ (builtins.foldl' (
          acc: tag:
          let
            # For error printing
            availableTags = lib.foldlAttrs (
              acc: _: v:
              v.tags or [ ] ++ acc
            ) [ ] (machines);

            tagMembers = builtins.attrNames (lib.filterAttrs (_n: v: builtins.elem tag v.tags or [ ]) machines);
          in
          if tagMembers == [ ] then
            lib.warn ''
              Service instance '${instanceName}': - ${roleName} tags: no machine with tag '${tag}' found.
              Available tags: ${builtins.toJSON (lib.unique availableTags)}
            '' acc
          else
            acc ++ tagMembers
        ) [ ] members.tags or [ ]);
    };
  /**
    Checks whether a module has a specific class

    # Arguments
    - `module` The module to check.

    # Returns
    - `string` | null: The specified class, or null if the class is not set

    # Throws
    - If the module is not a valid module
    - If the module has a type that is not supported
  */
  getModuleClass =
    module:
    let
      loadModuleForClassCheck =
        m:
        # Logic path adapted from nixpkgs/lib/modules.nix
        if lib.isFunction m then
          let
            args = lib.functionArgs m;
          in
          m args
        else if lib.isAttrs m then
          # module doesn't have a _type attribute
          if m._type or "module" == "module" then
            m
          # module has a _type set but it is not "module"
          else if m._type == "if" || m._type == "override" then
            throw "Module modifiers are not supported yet. Got: ${m._type}"
          else
            throw "Unsupported module type ${lib.typeOf m}"
        else if lib.isList m then
          throw "Invalid or unsupported module type ${lib.typeOf m}"
        else
          import m;

      loaded = loadModuleForClassCheck module;
    in
    if loaded ? _class then loaded._class else null;
}
