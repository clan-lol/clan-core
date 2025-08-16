{
  self,
  options,
  ...
}:
{
  imports = [
    ./distributed-service/flake-module.nix
  ];
  perSystem =
    {
      pkgs,
      lib,
      self',
      ...
    }:
    {
      devShells.inventory-schema = pkgs.mkShell {
        name = "clan-inventory-schema";
        inputsFrom = [
          self'.devShells.default
        ];
      };

      legacyPackages.schemas = (
        import ./schemas {
          flakeOptions = options;
          inherit
            pkgs
            self
            lib
            self'
            ;
        }
      );

      legacyPackages.clan-service-module-interface =
        (pkgs.nixosOptionsDoc {
          options =
            (self.clanLib.evalService {
              modules = [ { _docs_rendering = true; } ];
              prefix = [ ];
            }).options;
          warningsAreErrors = true;
          transformOptions = self.clanLib.docs.stripStorePathsFromDeclarations;
        }).optionsJSON;
    };
}
