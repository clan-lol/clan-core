{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/packages";
  manifest.description = "Define package sets from nixpkgs and install them on one or more machines";
  manifest.categories = [
    "System"
  ];

  roles.default = {
    description = "Placeholder role to apply the packages service";
    interface =
      { lib, ... }:
      {
        options.packages = lib.mkOption {

          type = lib.types.listOf lib.types.str;
          default = [ ];
          example = [ "cowsay" ];
          description = "The packages to install on the machine";
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            lib,
            pkgs,
            ...
          }:
          {

            environment.systemPackages = map (
              pName: lib.getAttrFromPath (lib.splitString "." pName) pkgs
            ) settings.packages;
          };
      };
  };

}
