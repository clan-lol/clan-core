{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/importer";
  manifest.description = "Convenient, structured module imports for hosts.";
  manifest.categories = [ "Utility" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = { };
}
