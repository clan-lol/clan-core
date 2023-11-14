{ config, lib, pkgs, ... }:
{
  options.clan.networking.meshnamed = {
    enable = (lib.mkEnableOption "meshnamed") // {
      default = config.clan.networking.meshnamed.networks != { };
    };
    networks = lib.mkOption {
      default = { };
      type = lib.types.attrsOf (lib.types.submodule ({ name, ... }: {
        options = {
          name = lib.mkOption {
            default = name;
            type = lib.types.str;
            example = "my-network";
            description = lib.mdDoc ''
              The name of the network.
            '';
          };
          subnet = lib.mkOption {
            type = lib.types.str;
            example = "fd43:7def:4b50:28d0:4e99:9347:3035:17ef/88";
            description = lib.mdDoc ''
              The subnet to use for the mesh network.
            '';
          };
        };
      }));
    };
  };
  config = lib.mkIf config.clan.networking.meshnamed.enable {
    systemd.services.meshnamed =
      let
        networks = lib.concatMapStringsSep "," (network: "${network.name}=${network.subnet}")
          (builtins.attrValues config.clan.networking.meshnamed.networks);
      in
      {
        wantedBy = [ "multi-user.target" ];
        after = [ "network.target" ];
        serviceConfig = {
          Type = "simple";
          ExecStart = "${pkgs.callPackage ../../../pkgs/meshname/default.nix { }}/bin/meshnamed -networks ${networks}";
          DynamicUser = true;
        };
      };
  };
}
