{ lib, ... }:
let
  eval =
    module:
    (lib.evalModules {
      modules = [
        ../default.nix
        module
      ];
    }).config;
in
{
  single_file_single_prompt =
    let
      config = eval {
        clan.core.vars.generators.my_secret = {
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
      test_file_secret_by_default = {
        expr = config.clan.core.vars.generators.my_secret.files.password.secret;
        expected = true;
      };
      test_secret_value_access_raises_error = {
        expr = config.clan.core.vars.generators.my_secret.files.password.value;
        expectedError.type = "ThrownError";
        expectedError.msg = "Cannot access value of secret file";
      };
      test_public_value_access = {
        expr = config.clan.core.vars.generators.my_secret.files.username ? value;
        expected = true;
      };
      # both secret and public values must provide a path
      test_secret_has_path = {
        expr = config.clan.core.vars.generators.my_secret.files.password ? path;
        expected = true;
      };
      test_public_var_has_path = {
        expr = config.clan.core.vars.generators.my_secret.files.username ? path;
        expected = true;
      };
    };
}
