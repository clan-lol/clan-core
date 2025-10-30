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
  test_not_defined =
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

  test_no_nested_imports =
    let
      eval = evalSettingsModule {
        foo = {
          imports = [ ];
        };
      };
    in
    {
      inherit eval;
      expr = eval.config.foo;
      expectedError = {
        type = "ThrownError";
        message = "*nested imports";
      };
    };

  test_no_function_modules =
    let
      eval = evalSettingsModule {
        foo =
          { ... }:
          {

          };
      };
    in
    {
      inherit eval;
      expr = eval.config.foo;
      expectedError = {
        type = "TypeError";
        message = "cannot convert a function to JSON";
      };
    };

  test_non_attrs_module =
    let
      eval = evalSettingsModule {
        foo = "foo.nix";
      };
    in
    {
      inherit eval;
      expr = eval.config.foo;
      expectedError = {
        type = "ThrownError";
        message = ".*foo.* is not of type";
      };
    };
}
