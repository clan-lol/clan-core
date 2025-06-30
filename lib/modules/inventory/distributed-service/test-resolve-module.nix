# Run: nix-unit ./test-resolve-module.nix
{
  lib ? import <nixpkgs/lib>,
}:
let
  resolveModule = import ./resolveModule.nix { inherit lib; };

  fromSpec =
    moduleSpec:
    resolveModule {
      inherit moduleSpec;
      flakeInputs = {
        self.clan.modules = {
          foo = {
            name = "self/foo";
          };
        };
      };
      clanCoreModules = {
        foo = {
          name = "clan/foo";
        };
        bar = {
          name = "clan/bar";
        };
      };
    };

in
{
  test_default_clan_core = {
    expr = fromSpec {
      name = "foo";
      input = null;
    };
    expected = {
      name = "clan/foo";
    };
  };
  test_self_module = {
    expr = fromSpec {
      name = "foo";
      input = "self";
    };
    expected = {
      name = "self/foo";
    };
  };
  test_missing_self_module = {
    expr = fromSpec {
      name = "bar";
      input = "self";
    };
    expectedError = {
      type = "ThrownError";
      msg = "flake input 'self' doesn't provide clan-module with name 'bar'";
    };
  };
  test_missing_core_module = {
    expr = fromSpec {
      name = "nana";
      input = null;
    };
    expectedError = {
      type = "ThrownError";
      msg = "clan-core doesn't provide clan-module with name 'nana'";
    };
  };
}
