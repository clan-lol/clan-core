{ lib, ... }:
let
  # {
  #   roles = {
  #     client = {
  #       machines = [
  #         "camina_machine"
  #         "vi_machine"
  #       ];
  #     };
  #     server = {
  #       machines = [ "vyr_machine" ];
  #     };
  #   };
  # }
  instanceOptions = lib.types.submodule {
    options.roles = lib.mkOption { type = lib.types.attrsOf machinesList; };
  };

  # {
  #   machines = [
  #     "camina_machine"
  #     "vi_machine"
  #     "vyr_machine"
  #   ];
  # }
  machinesList = lib.types.submodule {
    options.machines = lib.mkOption { type = lib.types.listOf lib.types.str; };
  };
in
{
  # clan.inventory.${moduleName}.${instanceName} = { ... }
  options.clan.services = lib.mkOption {
    type = lib.types.attrsOf (lib.types.attrsOf instanceOptions);
  };
}
