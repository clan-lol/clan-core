{ createTestClan, ... }:
let
  # Authored module
  # A minimal module looks like this
  # It isn't exactly doing anything but it's a valid module that produces an output
  modules."A" = {
    _class = "clan.service";
    manifest = {
      name = "network";
    };
  };

  modules."B" =
    { ... }:
    {
      options.stuff = "legacy-clan-service";
    };

  machines = {
    jon = { };
    sara = { };
  };

  resolve =
    spec:
    createTestClan {
      inherit modules;
      inventory = {
        inherit machines;
        instances."instance_foo" = {
          module = spec;
        };
      };
    };
in
{
  test_import_local_module_by_name = {
    expr =
      (resolve {
        name = "A";
        input = "self";
      }).config._services.mappedServices.self-A.manifest.name;
    expected = "network";
  };
  test_import_remote_module_by_name = {
    expr =
      (resolve {
        name = "uzzi";
        input = "upstream";
      }).config._services.mappedServices.upstream-uzzi.manifest.name;
    expected = "uzzi-from-upstream";

  };
}
