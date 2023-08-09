/*
  An example nixos module declaring an interface.
*/
{ lib, ... }: {
  options = {
    name = lib.mkOption {
      type = lib.types.str;
      default = "John Doe";
      description = "The name of the user";
    };
    age = lib.mkOption {
      type = lib.types.int;
      default = 42;
      description = "The age of the user";
    };
    isAdmin = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = "Is the user an admin?";
    };
    # a submodule option
    services = lib.mkOption {
      type = lib.types.submodule {
        options.opt = lib.mkOption {
          type = lib.types.str;
          default = "foo";
          description = "A submodule option";
        };
      };
    };
    userIds = lib.mkOption {
      type = lib.types.attrsOf lib.types.int;
      description = "Some attributes";
      default = {
        horst = 1;
        peter = 2;
        albrecht = 3;
      };
    };
    kernelModules = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "nvme" "xhci_pci" "ahci" ];
      description = "A list of enabled kernel modules";
    };
  };
}
