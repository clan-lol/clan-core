{ self, inputs, ... }:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
in
{
  perSystem =
    {
      pkgs,
      system,
      lib,
      ...
    }:
    let
      tests = import ./test.nix { inherit lib; };
    in
    {
      legacyPackages.evalTests-values = tests;

      # Run: nix build .#legacyPackages.x86_64-linux.evalCheck-eval-lib-values
      legacyPackages.evalCheck-eval-lib-values = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-lib-values";
        flakeAttr = "${
          self.filter {
            name = "lib";
            include = [
              "flake.nix"
              "flakeModules"
              "lib"
            ];
          }
        }#legacyPackages.${system}.evalTests-values";
      };
    };
}
