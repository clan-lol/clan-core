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
  imports = [
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
    }
    (lib.optionalAttrs (_class == "nixos") {
      clan.core.settings = {
        inherit (meta) name icon;
        inherit directory;
        machine = {
          inherit name;
        };
      };
    })
    # TODO: move into nixos modules
    ({
      networking.hostName = lib.mkDefault name;
    })
  ];
}
