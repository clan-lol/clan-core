{ lib, pkgs, ... }:
let
  eval =
    module:
    (lib.evalModules {
      modules = [
        ../interface.nix
        module
      ];
      specialArgs.pkgs = pkgs;
    }).config;

  usage_simple = {
    generators.my_secret = {
      files.password = { };
      files.username.secret = false;
      prompts.prompt1 = { };
      script = ''
        cp $prompts/prompt1 $files/password
      '';
    };
  };
in
{
  single_file_single_prompt =
    let
      config = eval usage_simple;
    in
    {
      # files are always secret by default
      test_file_secret_by_default = {
        expr = config.generators.my_secret.files.password.secret;
        expected = true;
      };
      # secret files must not provide a value
      test_secret_value_access_raises_error = {
        expr = config.generators.my_secret.files.password.value;
        expectedError.type = "ThrownError";
        expectedError.msg = "Cannot access value of secret file";
      };
      # public values must provide a value at eval time
      test_public_value_access = {
        expr = config.generators.my_secret.files.username ? value;
        expected = true;
      };
      # both secret and public values must provide a path
      test_secret_has_path = {
        expr = config.generators.my_secret.files.password ? path;
        expected = true;
      };
      test_public_var_has_path = {
        expr = config.generators.my_secret.files.username ? path;
        expected = true;
      };
    };

  # script can be text
  test_script_text =
    let
      config = eval {
        # imports = [ usage_simple ];
        generators.my_secret.script = ''
          echo "Hello, world!"
        '';
      };
    in
    {
      expr = config.generators.my_secret.script;
      expected = "echo \"Hello, world!\"\n";
    };

  # script can be a derivation
  test_script_writer =
    let
      config = eval {
        # imports = [ usage_simple ];
        generators.my_secret.script = derivation {
          system = pkgs.system;
          name = "my-script";
          builder = "/bin/sh";
          args = [
            "-c"
            ''touch $out''
          ];
        };
      };
    in
    {
      expr = lib.hasPrefix builtins.storeDir config.generators.my_secret.script;
      expected = true;
    };

  # test for mode attribute
  test_mode_attribute =
    let
      config = eval {
        generators.my_secret = {
          files.password = {
            mode = "0400";
          };
          script = ''
            echo "Mode set to ${config.generators.my_secret.files.password.mode}"
          '';
        };
      };
    in
    {
      expr = config.generators.my_secret.files.password.mode;
      expected = "0400";
    };
}
