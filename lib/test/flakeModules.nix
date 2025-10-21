{ lib, clanLib }:
{

  /**
    This function is used to create a module that can be imported into flake-parts
    and used to run eval tests.

    Usage: `lib.modules.importApply makeEvalChecks { module = module-under-test; testArgs = { }; }`

    returns a module to be imported into flake-parts

    Which in turn adds to the flake:

    - legacyPackages.<system>.eval-tests-<testName>: The attribute set passed to nix-unit. (Exposed for debugging i.e. via nix repl).
    - checks.<system>.eval-tests-<testName>: A derivation that can be built and fails if nix-unit fails
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
      attrName = "eval-tests-${testName}";
    in
    {
      pkgs,
      system,
      ...
    }:
    {
      legacyPackages.${attrName} = import tests (
        {
          inherit clanLib lib module;
        }
        // testArgs
      );
      checks.${attrName} =
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
        pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
          export HOME="$(realpath .)"

          nix-unit --eval-store "$HOME" \
            --extra-experimental-features flakes \
            --show-trace \
            ${inputOverrides} \
            --flake ${src}#legacyPackages.${system}.${attrName}
          touch $out
        '';

    };
}
