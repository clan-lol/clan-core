{
  lib,
  ...
}:
let
  inherit (lib) types;
in
{
  options = {
    age.plugins = lib.mkOption {
      type = types.listOf (types.strMatching "age-plugin-.*");
      default = [ ];
      description = ''
        A list of age plugins which must be available in the shell when encrypting and decrypting secrets.
      '';
    };
  };
}
