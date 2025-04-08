{ callInventoryAdapter, ... }:
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
    callInventoryAdapter {
      inherit modules machines;
      instances."instance_foo" = {
        module = spec;
      };
    };
in
{
  test_import_local_module_by_name = {
    expr = (resolve { name = "A"; }).importedModuleWithInstances.instance_foo.resolvedModule;
    expected = {
      _class = "clan.service";
      manifest = {
        name = "network";
      };
    };
  };
  test_import_remote_module_by_name = {
    expr =
      (resolve {
        name = "uzzi";
        input = "upstream";
      }).importedModuleWithInstances.instance_foo.resolvedModule;
    expected = {
      _class = "clan.service";
      manifest = {
        name = "uzzi-from-upstream";
      };
    };
  };
}
