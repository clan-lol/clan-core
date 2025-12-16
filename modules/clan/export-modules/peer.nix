{ name, lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types)
    str
    listOf
    attrTag
    submodule
    path
    ;
in
{
  options = {
    name = mkOption {
      type = str;
      default = name;
    };
    SSHOptions = mkOption {
      type = listOf str;
      default = [ ];
    };
    hosts = mkOption {
      description = ''
        Hosts to export for.

        Each entry can be either a hostname (plain string) or an attribute set (reference to a 'var')
      '';
      type = listOf (attrTag {
        plain = mkOption {
          type = str;
          description = ''
            a plain value, which can be read directly from the config
          '';
        };
        var = mkOption {
          description = ''
            A reference to a 'var' file

            The 'var' will be read by the CLI and potentially other services

            !!! Danger
                Don't export references to private vars.

                Their value cannot be accessed.
          '';
          type = submodule {
            options = {
              machine = mkOption {
                type = str;
                example = "jon";
              };
              generator = mkOption {
                type = str;
                example = "tor-ssh";
              };
              file = mkOption {
                type = str;
                example = "hostname";
              };
              flake = mkOption {
                type = path;
                example = "config.clan.core.settings.directory";
              };
            };
          };
        };
      });
    };
  };
}
