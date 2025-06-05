{ ... }:
{
  _class = "clan.service";
  manifest.name = "importer";
  manifest.description = "Convenient, structured module imports for hosts.";
  manifest.categories = [ "Utility" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = { };
}
