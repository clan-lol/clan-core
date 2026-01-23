{ lib, ... }:
{
  options.generators = lib.mkOption {
    default = { };
    type = lib.types.attrsOf (
      lib.types.deferredModuleWith {
        staticModules = [
          {
            options.dependencies = lib.mkOption {
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
              type = lib.types.attrsOf lib.types.raw;
              default = { };
            };
          }
          ./generator.nix
        ];
      }
    );
  };
}
