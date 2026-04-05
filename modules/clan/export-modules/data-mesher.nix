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

  options.namespaces = lib.mkOption {
    type = lib.types.listOf lib.types.str;
    default = [ ];
    description = ''
      List of namespace names for certificate-based file authorization.
      When configured, files named {namespace}/{signer_public_key_url_encoded}
      are permitted from any peer with a valid certificate signed by this network.
    '';
  };
}
