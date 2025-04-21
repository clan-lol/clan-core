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
      self,
      inputs,
      testName,
      tests,
      module,
      testArgs ? { },
    }:
    let
      inputOverrides = builtins.concatStringsSep " " (
        builtins.map (input: " --override-input ${input} ${inputs.${input}}") (builtins.attrNames inputs)
      );
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
      checks.${attrName} = pkgs.runCommand "tests" { nativeBuildInputs = [ pkgs.nix-unit ]; } ''
        export HOME="$(realpath .)"

        nix-unit --eval-store "$HOME" \
          --extra-experimental-features flakes \
          --show-trace \
          ${inputOverrides} \
          --flake ${self}#legacyPackages.${system}.${attrName}
        touch $out
      '';

    };
}
