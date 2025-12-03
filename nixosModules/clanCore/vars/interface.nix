{
  _class,
  lib,
  config,
  pkgs,
  ...
}:
let
  inherit (builtins)
    hashString
    toJSON
    ;
  inherit (lib)
    mkOption
    ;
  inherit (lib.types)
    attrsOf
    bool
    either
    enum
    int
    listOf
    nullOr
    oneOf
    package
    path
    str
    strMatching
    submoduleWith
    ;
  # the original types.submodule has strange behavior
  submodule =
    module:
    submoduleWith {
      modules = [ module ];
    };

  submoduleWithPkgs =
    module:
    submoduleWith {
      modules = [
        module
        { config._module.args.pkgs = pkgs; }
      ];
    };
  # Display module for prompts
  displayModule = {
    options = {
      display.group = mkOption {
        type = nullOr str;
        description = ''
          The group to display the prompt in.
          This is useful to group prompts together.
        '';
        default = null;
      };
      display.label = mkOption {
        type = nullOr str;
        description = ''
          The label to display for the prompt.
          If not set, the name of the prompt will be used.
        '';
        default = null;
      };
      display.required = mkOption {
        type = bool;
        description = ''
          Whether the prompt is required.
          If set to false, the user will be able to continue without providing a value.
        '';
        default = true;
      };
      display.helperText = mkOption {
        type = nullOr str;
        description = ''
          Additional text to display next to the prompt.
          This can be used to provide additional information about the prompt.
        '';
        default = null;
      };
    };
  };
in
{
  options = {
    settings = import ./settings-opts.nix { inherit lib; };
    generators = mkOption {
      description = ''
        A set of generators that can be used to generate files.
        Generators are scripts that produce files based on the values of other generators and user input.
        Each generator is expected to produce a set of files under a directory.
      '';
      default = { };
      type = attrsOf (
        submoduleWithPkgs (generator: {
          imports = [
            ./generator.nix
            (pkgs.path + "/nixos/modules/misc/assertions.nix")
            (lib.mkRemovedOptionModule [ "migrateFact" ] ''
              The `migrateFact` option has been removed.
              The facts system has been fully removed from clan-core.
              See https://docs.clan.lol/guides/migrations/migration-facts-vars/ for manual migration instructions.
            '')
          ];
          options = {
            name = mkOption {
              type = str;
              description = ''
                The name of the generator.
                This name will be used to refer to the generator in other generators.
              '';
              readOnly = true;
              default = generator.config._module.args.name;
              defaultText = "Name of the generator";
            };
            dependencies = mkOption {
              description = ''
                A list of other generators that this generator depends on.
                The output values of these generators will be available to the generator script as files.

                For example:

                **A file `file1` of a generator named `dep1` will be available via `$in/dep1/file1`**
              '';
              type = config.settings.dependenciesType;
              default = [ ];
            };
            validation = mkOption {
              description = ''
                A set of values that invalidate the generated values.
                If any of these values change, the generated values will be re-generated.
                Lists are not allowed as of now due to potential ordering issues
              '';
              default = null;
              # This is more restrictive than json without lists, but currently
              # if a value contains a list, we get an infinite recursion which
              # is hard to understand.
              type = nullOr (oneOf [
                bool
                int
                str
                (attrsOf (oneOf [
                  bool
                  int
                  str
                  (attrsOf (oneOf [
                    bool
                    int
                    str
                  ]))
                ]))
              ]);
            };
            # the validationHash is the validation interface to the outside world
            validationHash = mkOption {
              internal = true;
              description = ''
                A hash of the invalidation data.
                If the hash changes, the generated values will be re-generated.
              '';
              type = nullOr str;
              # TODO: recursively traverse the structure and sort all lists in order to support lists
              default =
                # For backwards compat, the hash is null by default in which case the check is omitted
                if generator.config.validation == null then
                  null
                else
                  hashString "sha256" (toJSON generator.config.validation);
              defaultText = "Hash of the invalidation data";
            };
            files = mkOption {
              description = ''
                A set of files to generate.
                The generator 'script' is expected to produce exactly these files under $out.
              '';
              type = attrsOf (
                submodule (file: {
                  imports = [
                    config.settings.fileModule
                    (lib.mkRenamedOptionModule
                      [
                        "sops"
                        "owner"
                      ]
                      [
                        "owner"
                      ]
                    )
                    (lib.mkRenamedOptionModule
                      [
                        "sops"
                        "group"
                      ]
                      [
                        "group"
                      ]
                    )
                  ];
                  options = {
                    name = mkOption {
                      type = str;
                      description = ''
                        name of the public fact
                      '';
                      readOnly = true;
                      default = file.config._module.args.name;
                      defaultText = "Name of the file";
                    };
                    generatorName = mkOption {
                      type = str;
                      description = ''
                        name of the generator
                      '';
                      readOnly = true;
                      default = generator.config._module.args.name;
                      defaultText = "Name of the generator that generates this file";
                    };
                    share = mkOption {
                      type = bool;
                      description = ''
                        Whether the generated vars should be shared between machines.
                        Shared vars are only generated once, when the first machine using it is deployed.
                        Subsequent machines will re-use the already generated values.
                      '';
                      readOnly = true;
                      internal = true;
                      default = generator.config.share;
                      defaultText = "Mirror of the share flag of the generator";
                    };
                    deploy = mkOption {
                      description = ''
                        Whether the file should be deployed to the target machine.

                        Disable this if the generated file is only used as an input to other generators.
                      '';
                      type = bool;
                      default = true;
                    };
                    secret = mkOption {
                      description = ''
                        Whether the file should be treated as a secret.
                      '';
                      type = bool;
                      default = true;
                    };
                    flakePath = mkOption {
                      description = ''
                        The path to the file containing the content of the generated value.
                        This will be set automatically
                      '';
                      type = nullOr path;
                      default = null;
                    };
                    path = mkOption {
                      description = ''
                        The path to the file containing the content of the generated value.
                        This will be set automatically
                      '';
                      type = str;
                      defaultText = ''
                        builtins.path {
                          name = "$${generator.config._module.args.name}_$${file.config._module.args.name}";
                          path = file.config.flakePath;
                        }
                      '';
                      default = builtins.path {
                        name = "${generator.config._module.args.name}_${file.config._module.args.name}";
                        path = file.config.flakePath;
                      };
                    };
                    neededFor = mkOption {
                      description = ''
                        This option determines when the secret will be decrypted and deployed to the target machine.

                        By setting this to `partitioning`, the secret will be deployed prior to running `disko` allowing
                        you to manage filesystem encryption keys. These will only be deployed when installing the system.
                        By setting this to `activation`, the secret will be deployed prior to running `nixos-rebuild` or `nixos-install`.
                        By setting this to `user`, the secret will be deployed prior to users and groups are created, allowing
                        users' passwords to be managed by vars. The secret will be stored in `/run/secrets-for-users` and `owner` and `group` must be `root`.
                      '';
                      type = enum [
                        "partitioning"
                        "activation"
                        "users"
                        "services"
                      ];
                      default = "services";
                    };
                    owner = mkOption {
                      description = "The user name or id that will own the file.";
                      type = str;
                      default = "root";
                    };
                    group = mkOption {
                      type = str;
                      description = "The group name or id that will own the file.";
                      default = if _class == "darwin" then "wheel" else "root";
                      defaultText = lib.literalExpression ''if _class == "darwin" then "wheel" else "root"'';
                    };
                    mode = mkOption {
                      type = strMatching "^[0-7]{4}$";
                      description = "The unix file mode of the file. Must be a 4-digit octal number.";
                      default = "0400";
                    };
                    exists = mkOption {
                      description = ''
                        Returns true if the file exists, This is used to guard against reading not set value in evaluation.
                        This currently only works for non secret files.
                      '';
                      type = bool;
                      default = if file.config.secret then throw "Cannot determine existance of secret file" else false;
                      defaultText = "Throws error because the existance of a secret file cannot be determined";
                    };
                    value =
                      mkOption {
                        description = ''
                          The content of the generated value.
                          Only available if the file is not secret.
                        '';
                        type = str;
                        defaultText = "Throws error because the value of a secret file is not accessible";
                      }
                      // lib.optionalAttrs file.config.secret {
                        default = throw "Cannot access value of secret file";
                      };
                  }
                  // (lib.optionalAttrs (_class == "nixos") {
                    restartUnits = mkOption {
                      description = ''
                        A list of systemd units that should be restarted after the file is deployed.
                        This is useful for services that need to reload their configuration after the file is updated.

                        WARNING: currently only sops-nix implements this option.
                      '';
                      type = listOf str;
                      default = [ ];
                    };
                  });
                })
              );
            };
            prompts = mkOption {
              description = ''
                A set of prompts to ask the user for values.
                Prompts are available to the generator script as files.
                For example, a prompt named 'prompt1' will be available via $prompts/prompt1
              '';
              default = { };
              type = attrsOf (
                submodule (prompt: {
                  imports = [ displayModule ];
                  options = {
                    name = mkOption {
                      description = ''
                        The name of the prompt.
                        This name will be used to refer to the prompt in the generator script.
                      '';
                      type = str;
                      default = prompt.config._module.args.name;
                      defaultText = "Name of the prompt";
                    };
                    persist = mkOption {
                      description = ''
                        Whether the prompted value should be stored in a file with the same name as the prompt.

                        If enabled, the behavior is equivalent to the following configuration:
                        ```nix
                        {
                          files.<name>.secret = true;
                          script = "cp $prompts/<name> $out/<name>";
                        }
                        ```
                      '';
                      type = bool;
                      default = false;
                    };
                    description = mkOption {
                      description = ''
                        The description of the prompted value
                      '';
                      type = str;
                      example = "SSH private key";
                      default = prompt.config._module.args.name;
                      defaultText = "Name of the prompt";
                    };
                    type = mkOption {
                      description = ''
                        The input type of the prompt.
                        The following types are available:
                          - hidden: A hidden text (e.g. password)
                          - line: A single line of text
                          - multiline: A multiline text
                          - multiline-hidden: A multiline text
                      '';
                      type = enum [
                        "hidden"
                        "line"
                        "multiline"
                        "multiline-hidden"
                      ];
                      default = "line";
                    };
                  };
                })
              );
            };
            runtimeInputs = mkOption {
              description = ''
                A list of packages that the generator script requires.
                These packages will be available in the PATH when the script is run.
              '';
              type = listOf package;
              default = [ ];
            };
            script = mkOption {
              description = ''
                The script to run to generate the files.
                The script will be run with the following environment variables:

                - $in: The directory containing the output values of all declared dependencies
                - $out: The output directory to put the generated files
                - $prompts: The directory containing the prompted values as files

                The script should produce the files specified in the 'files' attribute under $out.
              '';
              type = either str path;
              default = "";
            };
            finalScript = mkOption {
              description = ''
                The final generator script, wrapped, so:
                  - all required programs are in PATH
                  - sandbox is set up correctly
              '';
              type = path;
              readOnly = true;
              internal = true;
            };
            share = mkOption {
              description = ''
                Whether the generated vars should be shared between machines.
                Shared vars are only generated once, when the first machine using it is deployed.
                Subsequent machines will re-use the already generated values.
              '';
              type = bool;
              default = false;
            };
          };
        })
      );
    };
  };
}
