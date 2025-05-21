{ lib, clanLib, ... }:
let
  evalSettingsModule =
    m:
    lib.evalModules {
      modules = [
        {
          options.foo = lib.mkOption {
            type = clanLib.types.uniqueDeferredSerializableModule;
          };
        }
        m
      ];
    };
in
{
  test_1 =
    let
      eval = evalSettingsModule {
        foo = { };
      };
    in
    {
      inherit eval;
      expr = eval.config.foo;
      expected = {
        # Foo has imports
        # This can only ever be one module due to the type of foo
        imports = [
          {
            # This is the result of 'setDefaultModuleLocation'
            # Which also returns exactly one module
            _file = "<unknown-file>, via option foo";
            imports = [
              { }
            ];
          }
        ];
      };
    };
}
