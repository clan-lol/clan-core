{ lib, ... }:
{
  options.files = lib.mkOption {
    type = lib.types.attrsOf (lib.types.listOf lib.types.str);
    default = { };
    description = ''
      A mapping of file names to lists of base64-encoded ED25519 public keys.
      These files will be distributed via data-mesher and must be signed
      by one of the configured public keys.
    '';
  };
}
