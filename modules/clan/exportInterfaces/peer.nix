(
  { lib, ... }:
  {
    options = {
      SSHOptions = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
      };
      hosts = lib.mkOption {
        description = '''';
        type = lib.types.listOf (
          lib.types.attrTag {
            plain = lib.mkOption {
              type = lib.types.str;
              description = ''
                a plain value, which can be read directly from the config
              '';
            };
            var = lib.mkOption {
              description = ''
                A reference to a 'var' file

                The 'var' will be read by the CLI and potentially other services

                !!! Danger
                    Don't export references to private vars.

                    Their value cannot be accessed.
              '';
              type = lib.types.submodule {
                options = {
                  machine = lib.mkOption {
                    type = lib.types.str;
                    example = "jon";
                  };
                  generator = lib.mkOption {
                    type = lib.types.str;
                    example = "tor-ssh";
                  };
                  file = lib.mkOption {
                    type = lib.types.str;
                    example = "hostname";
                  };
                };
              };
            };
          }
        );
      };
    };
  }
)
