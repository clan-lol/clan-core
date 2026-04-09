{ lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types)
    attrsOf
    attrs
    bool
    listOf
    nullOr
    str
    submodule
    ;
in
{
  options = {
    users = mkOption {
      type = attrsOf (submodule {
        options = {
          username = mkOption { type = str; };
          email = mkOption { type = str; };
          groups = mkOption {
            type = listOf str;
            default = [ ];
          };
          displayname = mkOption { type = str; };
        };
      });
      default = { };
      description = "IdP user identities keyed by IdP instance name (exported by the users service)";
    };

    client = mkOption {
      type = nullOr (submodule {
        options = {
          clientId = mkOption { type = str; };
          clientName = mkOption {
            type = str;
            default = "";
          };
          redirectUris = mkOption { type = listOf str; };
          scopes = mkOption {
            type = listOf str;
            default = [
              "openid"
              "profile"
              "email"
            ];
          };
          public = mkOption {
            type = bool;
            default = false;
          };
        };
      });
      default = null;
      description = "OIDC client registration (exported by consuming services)";
    };

    varsGenerator = mkOption {
      type = nullOr attrs;
      default = null;
      description = "Vars generator definition for the OIDC client secret (share=true attrset)";
    };
  };
}
