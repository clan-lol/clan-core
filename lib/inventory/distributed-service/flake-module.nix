{ self, inputs, ... }:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  perSystem =
    {
      pkgs,
      lib,
      system,
      ...
    }:
    let
      # Common filtered source for inventory tests
      inventoryTestsSrc = lib.fileset.toSource {
        root = ../../..;
        fileset = lib.fileset.unions [
          ../../../flake.nix
          ../../../flake.lock
          (lib.fileset.fileFilter (file: file.name == "flake-module.nix") ../../..)
          ../../../flakeModules
          ../../../lib
          ../../../nixosModules/clanCore
          ../../../nixosModules/machineModules
          ../../../machines
          ../../../inventory.json
          ../../../modules
        ];
      };
    in
    {
      # Run: nix-unit --extra-experimental-features flakes --flake .#legacyPackages.x86_64-linux.evalTests-distributedServices
      legacyPackages.evalTests-distributedServices = import ./tests {
        inherit lib;
        clanLib = self.clanLib;
      };

      # Run: nix build .#legacyPackages.x86_64-linux.evalCheck-eval-lib-distributedServices
      legacyPackages.evalCheck-eval-lib-distributedServices = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-lib-distributedServices";
        flakeAttr = "${inventoryTestsSrc}#legacyPackages.${system}.evalTests-distributedServices";
      };
    };
}
