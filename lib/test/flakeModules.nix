{ lib, clanLib }:
{

  /**
    This function is used to create a module that can be imported into flake-parts
    and used to run eval tests.

    Usage: `lib.modules.importApply makeEvalChecks { module = module-under-test; testArgs = { }; }`

    returns a module to be imported into flake-parts

    Which in turn adds to the flake:

    - legacyPackages.<system>.evalTests-<testName>: The attribute set passed to nix-unit. (Exposed for debugging i.e. via nix repl).
    - legacyPackages.<system>.evalCheck-eval-tests-<testName>: The nix-unit derivation for this test.

    All eval checks are collected into a single `checks.<system>.eval-tests` derivation
    (see checks/flake-module.nix). To run a single test manually:
      nix build .#legacyPackages.<system>.evalCheck-eval-tests-<testName>
  */
  makeEvalChecks =
    {
      fileset,
      inputs,
      testName,
      tests,
      module,
      testArgs ? { },
    }:
    let
      inputOverrides = clanLib.flake-inputs.getOverrides inputs;
      evalTestsAttr = "evalTests-${testName}";
      attrName = "eval-tests-${testName}";
    in
    {
      pkgs,
      system,
      ...
    }:
    {
      legacyPackages.${evalTestsAttr} = import tests (
        {
          inherit clanLib lib module;
        }
        // testArgs
      );
      legacyPackages.${"evalCheck-${attrName}"} =
        let
          # The root is two directories up from where this file is located
          root = ../..;

          # Combine the user-provided fileset with all flake-module.nix files
          # and other essential files
          src = lib.fileset.toSource {
            inherit root;
            fileset = lib.fileset.unions [
              # Core flake files
              (root + "/flake.nix")
              (root + "/flake.lock")

              # All flake-module.nix files anywhere in the tree
              (lib.fileset.fileFilter (file: file.name == "flake-module.nix") root)

              # The flakeModules/clan.nix if it exists
              (lib.fileset.maybeMissing (root + "/flakeModules/clan.nix"))

              # Core libraries
              (root + "/lib")

              # modules directory
              (root + "/modules")

              # User-provided fileset
              fileset
            ];
          };
        in
        clanLib.test.mkEvalCheck {
          inherit pkgs system inputOverrides;
          name = attrName;
          flakeAttr = "${src}#legacyPackages.${system}.${evalTestsAttr}";
        };

    };
}
