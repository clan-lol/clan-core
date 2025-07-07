{ ... }:
{
  /**
    Generate nix-unit input overrides for tests

    # Example
    ```nix
    inputOverrides = clanLib.flake-inputs.getOverrides inputs;
    ```
  */
  getOverrides =
    inputs:
    builtins.concatStringsSep " " (
      builtins.map (input: " --override-input ${input} ${inputs.${input}}") (
        builtins.filter (name: name != "self") (builtins.attrNames inputs)
      )
    );
}
