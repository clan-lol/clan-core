{
  lib,
  config,
  pkgs,
  ...
}:

let
  cfg = config.clan.wifi;

  inherit (lib)
    concatMapAttrsStringSep
    flip
    mapAttrs
    ;

  password_path =
    network_name: config.clan.core.vars.generators."iwd.${network_name}".files.password.path;

  ssid_path = network_name: config.clan.core.vars.generators."iwd.${network_name}".files.ssid.path;

  secret_generator = name: value: {
    name = "iwd.${name}";
    value = {
      prompts.ssid.type = "line";
      prompts.ssid.persist = true;
      prompts.password.type = "hidden";
      prompts.password.persist = true;
      share = true;
    };
  };
in
{
  options.clan.wifi = {
    networks = lib.mkOption {
      visible = false;
      type = lib.types.attrsOf (
        lib.types.submodule (
          { ... }:
          {
            options = {
              enable = lib.mkOption {
                type = lib.types.bool;
                default = true;
                description = "Enable this wifi network";
              };
              autoConnect = lib.mkOption {
                type = lib.types.bool;
                default = true;
                description = "Automatically try to join this wifi network";
              };
            };
          }
        )
      );
      default = { };
      description = "Wifi networks to predefine";
    };
  };

  config = lib.mkIf (cfg.networks != { }) {

    clan.core.vars.generators = lib.mapAttrs' secret_generator cfg.networks;

    networking.networkmanager.enable = true;

    networking.networkmanager.ensureProfiles.environmentFiles = [
      "/run/secrets/NetworkManager/wifi-secrets"
    ];

    networking.networkmanager.ensureProfiles.profiles = flip mapAttrs cfg.networks (
      name: _network: {
        connection.id = "$ssid_${name}";
        connection.type = "wifi";
        wifi.mode = "infrastructure";
        wifi.ssid = "$ssid_${name}";
        wifi-security.psk = "$pw_${name}";
        wifi-security.key-mgmt = "wpa-psk";
      }
    );

    # service to generate the environment file containing all secrets, as
    #   expected by the nixos NetworkManager-ensure-profile service
    systemd.services.NetworkManager-setup-secrets = {
      description = "Generate wifi secrets for NetworkManager";
      requiredBy = [ "NetworkManager-ensure-profiles.service" ];
      partOf = [ "NetworkManager-ensure-profiles.service" ];
      before = [ "NetworkManager-ensure-profiles.service" ];
      serviceConfig = {
        Type = "oneshot";
        ExecStart = pkgs.writeShellScript "wifi-secrets" ''
          set -euo pipefail

          env_file=/run/secrets/NetworkManager/wifi-secrets
          mkdir -p $(dirname "$env_file")
          : > "$env_file"

          # Generate the secrets file
          echo "Generating wifi secrets file: $env_file"
          ${flip (concatMapAttrsStringSep "\n") cfg.networks (
            name: _network: ''
              echo "ssid_${name}=\"$(cat "${ssid_path name}")\"" >> /run/secrets/NetworkManager/wifi-secrets
              echo "pw_${name}=\"$(cat "${password_path name}")\"" >> /run/secrets/NetworkManager/wifi-secrets
            ''
          )}
        '';
      };
    };
  };
}
