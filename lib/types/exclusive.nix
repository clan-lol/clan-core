{ lib, clanLib, ... }:
let
  test =
    ms:
    lib.evalModules {
      modules = [
        {
          options.exportsModule = lib.mkOption {
            type = clanLib.types.exclusiveDeferredModule {
              warning = ''
                Why this needs to be set only once
              '';
            };
          };
        }
      ]
      ++ ms;
    };
in
{
  test_set_once =
    let
      eval = test [
        # In clan-core
        {
          exportsModule = {
            options.foo = lib.mkOption { };
          };
        }
      ];
    in
    {
      inherit eval;
      expr = lib.deepSeq eval.config.exportsModule 1;
      expected = 1;
    };
  test_set_twice =
    let
      eval = test [
        # In clan-core
        {
          exportsModule = {
            options.foo = lib.mkOption { };
          };
        }
        # The user
        {
          exportsModule = {
            options.foo = lib.mkOption { };
            options.bar = lib.mkOption { };
          };
        }
      ];
    in
    {
      inherit eval;
      expr = lib.deepSeq eval.config.exportsModule 1;
      # cannot test the emited warnings unfortunately
      expected = 1;
    };
}
