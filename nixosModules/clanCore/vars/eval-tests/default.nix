{ lib, ... }:
let
  eval =
    module:
    (lib.evalModules {
      modules = [
        ../interface.nix
        module
      ];
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

  # Ensure that generators.imports works
  # This allows importing generators from third party projects without providing
  #   them access to other settings.
  test_generator_modules =
    let
      generator_module = {
        my-generator.files.password = { };
      };
      config = eval { generators.imports = [ generator_module ]; };
    in
    {
      expr = lib.trace (lib.attrNames config.generators) config.generators ? my-generator;
      expected = true;
    };
}
