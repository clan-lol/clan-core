{
  self,
  lib,
  flakeOptions,
  ...
}:
let
  opts = flakeOptions.flake.type.getSubOptions [ "flake" ];
  clanOpts = opts.clan.type.getSubOptions [ "clan" ];
  include = [
    "directory"
    "inventory"
    "machines"
    "meta"
    "modules"
    "outputs"
    "secrets"
    "templates"
  ];
  jsonschema = self.clanLib.jsonschema.fromOptions {
    typePrefix = "Clan";
    output = true;
    readOnly = {
      input = false;
      output = true;
    };
    renamedTypes = {
      ClanInventory = "Inventory";
      InventoryTagsAll = "InventoryTagMachines";
      InventoryTagsDarwin = "InventoryTagMachines";
      InventoryTagsNixos = "InventoryTagMachines";
      InventoryTagsFreeform = "InventoryTagMachines";
      InventoryMachinesItem = "Machine";
      MachineMachineClass = "MachineClass";
      InventoryInstances = "Instances";
      InstanceRoleTagsFrom = "InstanceRoleTagList";
      InstanceRoleTagsTo = "InstanceRoleTagDict";
      InstanceRoleTagDictItem = "EmptyDict";
      ClanOutputs = "Outputs";
      ClanSecrets = "Secrets";
      InstancesItem = "Instance";
      InstanceRolesItem = "InstanceRole";
      InstanceRoleMachinesItem = "InstanceRoleMachine";
      ClanTemplates = "Templates";
      TemplatesClanItem = "TemplateClan";
      TemplatesMachineItem = "TemplateMachine";
      TemplatesDiskoItem = "TemplateDisko";
    };
  } (lib.filterAttrs (n: _v: lib.elem n include) clanOpts);
in
jsonschema
