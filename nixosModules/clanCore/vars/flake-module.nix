{
  self,
  inputs,
  lib,
  ...
}:
let
  inputOverrides = self.clanLib.flake-inputs.getOverrides inputs;
  varsFileset = lib.fileset.toSource {
    root = ../../..;
    fileset = lib.fileset.unions [
      ../../../flake.nix
      ../../../flake.lock
      (lib.fileset.fileFilter (file: file.name == "flake-module.nix") ../../..)
      ../../../flakeModules/clan.nix
      ../../../lib
      ../../../modules
      ../../../nixosModules/clanCore/vars
    ];
  };
in
{
  perSystem =
    { system, pkgs, ... }:
    {
      legacyPackages.evalTests-module-clan-vars = import ./eval-tests {
        inherit lib pkgs;
      };
      legacyPackages.evalTests-vars-backends = import ./eval-tests/backends.nix {
        inherit lib pkgs;
      };
      legacyPackages.evalTests-generators-to-sops = import ./secret/sops/generators-to-sops-test.nix {
        inherit lib;
      };
      # Run: nix build .#legacyPackages.x86_64-linux.evalCheck-eval-module-clan-vars
      legacyPackages.evalCheck-eval-module-clan-vars = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-module-clan-vars";
        flakeAttr = "${varsFileset}#legacyPackages.${system}.evalTests-module-clan-vars";
      };
      legacyPackages.evalCheck-eval-vars-backends = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-vars-backends";
        flakeAttr = "${varsFileset}#legacyPackages.${system}.evalTests-vars-backends";
      };
      legacyPackages.evalCheck-eval-generators-to-sops = self.clanLib.test.mkEvalCheck {
        inherit pkgs system inputOverrides;
        name = "eval-generators-to-sops";
        flakeAttr = "${varsFileset}#legacyPackages.${system}.evalTests-generators-to-sops";
      };
    };
}
