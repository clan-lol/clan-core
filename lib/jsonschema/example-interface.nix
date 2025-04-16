# An example nixos module declaring an interface.
{ lib, ... }:
{
  options = {
    # str
    name = lib.mkOption {
      type = lib.types.str;
      default = "John Doe";
      description = "The name of the user";
    };
    # int
    age = lib.mkOption {
      type = lib.types.int;
      default = 42;
      description = "The age of the user";
    };
    # bool
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
    # attrs of int
    userIds = lib.mkOption {
      type = lib.types.attrsOf lib.types.int;
      description = "Some attributes";
      default = {
        horst = 1;
        peter = 2;
        albrecht = 3;
      };
    };
    # attrs of submodule
    userModules = lib.mkOption {
      type = lib.types.attrsOf (
        lib.types.submodule {
          options.foo = lib.mkOption { };
        }
      );
    };
    # list of str
    kernelModules = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [
        "nvme"
        "xhci_pci"
        "ahci"
      ];
      description = "A list of enabled kernel modules";
    };
    # enum
    colour = lib.mkOption {
      type = lib.types.enum [
        "red"
        "blue"
        "green"
      ];
      default = "red";
      description = "The colour of the user";
    };
    destinations = lib.mkOption {
      type = lib.types.attrsOf (
        lib.types.submodule (
          { name, ... }:
          {
            options = {
              name = lib.mkOption {
                type = lib.types.strMatching "^[a-zA-Z0-9._-]+$";
                default = name;
                description = "the name of the backup job";
              };
              repo = lib.mkOption {
                type = lib.types.str;
                description = "the borgbackup repository to backup to";
              };
            };
          }
        )
      );
      default = { };
    };
  };
}
