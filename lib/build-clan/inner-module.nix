{
  system,
  name,
  pkgs,
  clanConfiguration,
}:
{
  _class,
  lib,
  ...
}:
let
  inherit (clanConfiguration) directory machines pkgsForSystem;
  inherit (clanConfiguration.clanInternals) inventoryClass;
in
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
      imports = (inventoryClass.machines.${name}.machineImports or [ ]);

      config = {
        clan.core.settings = {
          inherit (clanConfiguration.inventory.meta) name icon;

          inherit directory;
          machine = {
            inherit name;
          };
        };
        # Inherited from clan wide settings
        # TODO: remove these
      };
    })
    (
      {
        networking.hostName = lib.mkDefault name;

        # For vars we need to override the system so we run vars
        # generators on the machine that runs `clan vars generate`. If a
        # users is using the `pkgsForSystem`, we don't set
        # nixpkgs.hostPlatform it would conflict with the `nixpkgs.pkgs`
        # option.
        nixpkgs.hostPlatform = lib.mkIf (system != null && (pkgsForSystem system) != null) (
          lib.mkForce system
        );
      }
      // lib.optionalAttrs (pkgs != null) { nixpkgs.pkgs = lib.mkForce pkgs; }
    )
  ];
}
