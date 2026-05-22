{ ... }:
{
  _class = "clan.service";
  manifest.name = "importer";
  manifest.description = "Convenient, structured module imports for hosts.";
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "Placeholder role to apply the importer service";
  };
}
