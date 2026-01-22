{
  lib,
  ...
}:
let
  inherit (lib) types;

  # Type for age plugin specifications - either a nixpkgs package name or a flake reference
  agePluginType = types.strMatching "(age-plugin-.*|[^#]+#.+)";
in
{
  options = {
    age.plugins = lib.mkOption {
      type = types.listOf agePluginType;
      default = [ ];
      description = ''
        A list of age plugins which must be available in the shell when encrypting and decrypting secrets.

        Each entry can be either:
        - A package name from nixpkgs (e.g., `"age-plugin-yubikey"`)
        - A flake reference for packages not in nixpkgs (e.g., `"github:owner/repo#package"`)
      '';
      example = lib.literalExpression ''
        [
          "age-plugin-yubikey"  # from nixpkgs
          "github:pinpox/age-plugin-picohsm#default"  # custom flake
        ]
      '';
    };
  };
}
