{ lib, config, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types)
    str
    path
    bool
    nullOr
    ;

  fileModuleInterface = file: {
    options = {
      name = mkOption {
        type = str;
        description = ''
          name of the public fact
        '';
        readOnly = true;
        default = file.config._module.args.name;
        defaultText = "Name of the file";
      };
      generatorName = mkOption {
        type = str;
        description = ''
          name of the generator
        '';
        # This must be set by the 'generator' (parent of this submodule)
        default = throw "generatorName must be set by the generator";
        defaultText = "Name of the generator that generates this file";
      };
      secret = mkOption {
        description = ''
          Whether the file should be treated as a secret.
        '';
        type = bool;
        default = true;
      };
      flakePath = mkOption {
        description = ''
          The path to the file containing the content of the generated value.
          This will be set automatically
        '';
        type = nullOr path;
        default = null;
      };
      path = mkOption {
        description = ''
          The path to the file containing the content of the generated value.
          This will be set automatically
        '';
        type = str;
        defaultText = ''
          builtins.path {
            name = "$${file.config.generatorName}_$${file.config.name}";
            path = file.config.flakePath;
          }
        '';
        default =
          if file.config.flakePath == null then
            throw "flakePath must be set before accessing path"
          else
            builtins.path {
              name = "${file.config.generatorName}_${file.config.name}";
              path = file.config.flakePath;
            };
      };
      exists = mkOption {
        description = ''
          Returns true if the file exists. This is used to guard against reading not set value in evaluation.
          This currently only works for non secret files.
        '';
        type = bool;
        default = if file.config.secret then throw "Cannot determine existence of secret file" else false;
        defaultText = "Throws error because the existence of a secret file cannot be determined";
      };
      value =
        mkOption {
          description = ''
            The content of the generated value.
            Only available if the file is not secret.
          '';
          type = str;
          defaultText = "Throws error because the value of a secret file is not accessible";
        }
        // lib.optionalAttrs file.config.secret {
          default = throw "Cannot access value of secret file";
        };
    };
  };

in
{
  options = {
    secretStore = lib.mkOption {
      type = lib.types.enum [
        "sops"
        "password-store"
        "vm"
        "fs"
        "custom"
      ];
      default = "sops";
      description = ''
        method to store secret vars.
        custom can be used to define a custom secret var store.
      '';
    };

    secretModule = lib.mkOption {
      type = lib.types.str;
      internal = true;
      description = ''
        the python import path to the secret module
      '';
    };

    # TODO: see if this is the right approach. Maybe revert to secretPathFunction
    fileModule = lib.mkOption {
      type = lib.types.deferredModuleWith {
        staticModules = [
          fileModuleInterface
          (lib.mkRenamedOptionModule
            [
              "sops"
              "owner"
            ]
            [
              "owner"
            ]
          )
          (lib.mkRenamedOptionModule
            [
              "sops"
              "group"
            ]
            [
              "group"
            ]
          )
        ];
      };
      internal = true;
      description = ''
        A module to be imported in every vars.files.<name> submodule.
        Used by backends to define the `path` attribute.
      '';
      default = { };
    };

    publicStore = lib.mkOption {
      type = lib.types.enum [
        "in_repo"
      ];
      default = "in_repo";
      description = ''
        Method to store public vars.
        Currently only 'in_repo' is supported, which stores public vars in the clan repository.
      '';
    };

    publicModule = lib.mkOption {
      type = lib.types.str;
      internal = true;
      description = ''
        the python import path to the public module
      '';
    };
  };

  # TODO: Refactor this to use an explicit mapping instead of mkIf
  imports = [
    # SecretModules
    {

      secretModule = lib.mkIf (config.secretStore == "fs") "clan_lib.vars.secret_modules.fs";
    }
    {

      secretModule = lib.mkIf (config.secretStore == "sops") "clan_lib.vars.secret_modules.sops";
    }
    {
      secretModule = lib.mkIf (
        config.secretStore == "password-store"
      ) "clan_lib.vars.secret_modules.password_store";
    }
    {
      secretModule = lib.mkIf (config.secretStore == "vm") "clan_lib.vars.secret_modules.vm";
    }
    # PublicModules
    {
      publicModule = lib.mkIf (config.publicStore == "in_repo") "clan_lib.vars.public_modules.in_repo";
    }
  ];
}
