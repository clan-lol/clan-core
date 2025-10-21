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
              modules = [
                { _docs_rendering = true; }
                {
                  options."#specialArgs" = lib.mkOption {
                    description = ''
                      Adidtional arguments passed to the module. Often referred to as `specialArgs`.

                      ```nix
                      {
                        # root directory of the clan
                        directory,
                        # clanLib - The clan library functions
                        clanLib,
                        # exports from all services
                        exports,
                        ...
                      }:
                      {
                        _class = "clan.service";
                        manifest.name = "example-service";

                        # ... elided
                      }
                      ```
                    '';
                  };
                }
              ];
              prefix = [ ];
            }).options;
          warningsAreErrors = true;
          transformOptions = self.clanLib.docs.stripStorePathsFromDeclarations;
        }).optionsJSON;
    };
}
