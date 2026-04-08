{ lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types)
    attrsOf
    deferredModuleWith
    listOf
    raw
    str
    ;
  exportsFileModule = {
    options.deploy = mkOption {
      description = ''
        Whether the file should be deployed to the target machine.

        Disable this if the generated file is only used as an input to other generators.
      '';
      type = listOf str;
      # Deploy nowhere by default
      default = [ ];
    };
  };
in
{
  options.generators = mkOption {
    default = { };
    type = attrsOf (deferredModuleWith {
      staticModules = [
        {
          options.dependencies = mkOption {
            description = ''
              An attribute set of other generators that this generator depends on.

              Example:

              dependencies.jonB = declareDependency { generator = "B"; instance = "instanceB2"; ...; };
              =>
              script = "
                $in/jonB/file1
              ";

              The attribute name determines the path

              Each file of the generator B is available under that subpath
            '';
            type = attrsOf raw;
            default = { };
          };
        }
        (lib.modules.importApply ./generic-generator.nix { fileContextModule = exportsFileModule; })
      ];
    });
  };
}
