{ lib, clanLib, ... }:
let
  inherit (lib) evalModules mkOption;
  inherit (clanLib.types) record;
in
{
  test_simple =
    let
      eval = evalModules {
        modules = [
          {
            options.foo = mkOption {
              type = record { };
              default = { };
            };
          }
        ];
      };
    in
    {
      inherit eval;
      expr = eval.config.foo;
      expected = { };
    };

  test_wildcard =
    let
      eval = evalModules {
        modules = [
          {
            options.foo = mkOption {
              type = record { };
              default = { };
            };
          }
        ];
      };
    in
    {
      inherit eval;
      expr = eval.config.foo;
      expected = { };
    };
}
