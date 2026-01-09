{ lib, config, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types)
    str
    path
    bool
    nullOr
    deferredModuleWith
    submoduleWith
    attrsOf
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

  storeModule = {
    options.pythonModule = mkOption { type = str; };
  };

in
{
  options = {
    secretStore = mkOption {
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

    secretModule = mkOption {
      type = str;
      internal = true;
      description = ''
        the python import path to the secret module
      '';
      default = config.stores.${config.secretStore}.pythonModule;
    };

    # TODO: see if this is the right approach. Maybe revert to secretPathFunction
    fileModule = mkOption {
      type = deferredModuleWith {
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

    publicStore = mkOption {
      type = lib.types.enum [
        "in_repo"
      ];
      default = "in_repo";
      description = ''
        Method to store public vars.
        Currently only 'in_repo' is supported, which stores public vars in the clan repository.
      '';
    };

    publicModule = mkOption {
      type = str;
      internal = true;
      description = ''
        the python import path to the public module
      '';
      default = config.publicStores.${config.publicStore}.pythonModule;
    };

    stores = mkOption {
      internal = true;
      visible = false;
      type = attrsOf (submoduleWith {
        modules = [ storeModule ];
      });
    };
    publicStores = mkOption {
      internal = true;
      visible = false;
      type = attrsOf (submoduleWith {
        modules = [ storeModule ];
      });
    };
  };

  config.stores = {
    fs = {
      pythonModule = "clan_lib.vars.secret_modules.fs";
    };
    sops = {
      pythonModule = "clan_lib.vars.secret_modules.sops";
    };
    "password-store" = {
      pythonModule = "clan_lib.vars.secret_modules.password_store";
    };
    vm = {
      pythonModule = "clan_lib.vars.secret_modules.vm";
    };
  };
  config.publicStores = {
    in_repo = {
      pythonModule = "clan_lib.vars.public_modules.in_repo";
    };
  };
}
