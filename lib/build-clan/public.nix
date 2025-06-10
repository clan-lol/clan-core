/**
  Publicly exported attribute names
  These are mapped from 'options.clan.{name}' into 'flake.{name}'
  For example "clanInternals" will be exposed as "flake.clan.clanInternals"
  This list is used to guarantee equivalent attribute sets for both flake-parts and buildClan users.
*/
{
  # flake.clan.{name} <- clan.{name}
  clan = [
    "templates"
    "modules"
  ];
  # flake.{name} <- clan.{name}
  topLevel = [
    "clanInternals"
    "nixosConfigurations"
    "nixosModules"
    "darwinConfigurations"
    "darwinModules"
  ];
}
