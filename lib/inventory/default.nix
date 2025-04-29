{ lib, clanLib }:
let
  services = clanLib.callLib ./distributed-service/inventory-adapter.nix { };
in
{
  inherit (services) evalClanService mapInstances;
  inherit (import ./build-inventory { inherit lib clanLib; }) buildInventory;
  interface = ./build-inventory/interface.nix;
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
}
