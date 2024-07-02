{ lib, ... }:
{
  options = {
    secretStore = lib.mkOption {
      type = lib.types.enum [
        "sops"
        "password-store"
        "vm"
        "custom"
      ];
      default = "sops";
      description = ''
        method to store secret facts
        custom can be used to define a custom secret fact store.
      '';
    };

    secretModule = lib.mkOption {
      type = lib.types.str;
      internal = true;
      description = ''
        the python import path to the secret module
      '';
    };

    secretUploadDirectory = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      default = null;
      description = ''
        The directory where secrets are uploaded into, This is backend specific.
      '';
    };

    secretPathFunction = lib.mkOption {
      type = lib.types.raw;
      description = ''
        The function to use to generate the path for a secret.
        The default function will use the path attribute of the secret.
        The function will be called with the secret submodule as an argument.
      '';
    };

    publicStore = lib.mkOption {
      type = lib.types.enum [
        "in_repo"
        "vm"
        "custom"
      ];
      default = "in_repo";
      description = ''
        method to store public facts.
        custom can be used to define a custom public fact store.
      '';
    };

    publicModule = lib.mkOption {
      type = lib.types.str;
      internal = true;
      description = ''
        the python import path to the public module
      '';
    };

    publicDirectory = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      default = null;
    };
  };
}
