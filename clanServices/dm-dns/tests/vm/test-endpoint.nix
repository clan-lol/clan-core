{ ... }:
{
  _class = "clan.service";
  manifest.name = "test-endpoint";
  manifest.description = "Dummy endpoint service for dm-dns testing";
  manifest.readme = "Dummy readme to silence eval warnings.";
  manifest.exports.out = [ "endpoints" ];

  roles.default = {
    description = "Dummy description to silence eval warnings.";

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
