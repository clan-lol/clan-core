{
  name,
  directory,
  meta,
}:
{
  _class,
  lib,
  ...
}:
{
  imports = builtins.filter builtins.pathExists (
    [
      "${directory}/machines/${name}/configuration.nix"
    ]
    ++ lib.optionals (_class == "nixos") [
      "${directory}/machines/${name}/hardware-configuration.nix"
      "${directory}/machines/${name}/disko.nix"
    ]
  );

  clan.core.settings = {
    inherit (meta) name icon tld;
    inherit directory;
    machine = {
      inherit name;
    };
  };
}
