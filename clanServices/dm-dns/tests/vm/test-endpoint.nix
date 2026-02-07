{ ... }:
{
  _class = "clan.service";
  manifest.name = "test-endpoint";
  manifest.description = "Dummy endpoint service for dm-dns testing";
  manifest.exports.out = [ "endpoints" ];

  roles.default = {
    perInstance =
      { mkExports, ... }:
      {
        exports = mkExports {
          endpoints.hosts = [ "myapp.test" ];
        };

        nixosModule = { ... }: { };
      };
  };
}
