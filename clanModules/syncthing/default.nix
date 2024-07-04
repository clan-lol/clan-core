{
  config,
  pkgs,
  lib,
  ...
}:
{
  options.clan.syncthing = {
    id = lib.mkOption {
      description = ''
        The ID of the machine.
        It is generated automatically by default.
      '';
      type = lib.types.nullOr lib.types.str;
      example = "BABNJY4-G2ICDLF-QQEG7DD-N3OBNGF-BCCOFK6-MV3K7QJ-2WUZHXS-7DTW4AS";
      default = config.clan.core.facts.services.syncthing.public."syncthing.pub".value or null;
      defaultText = "config.clan.core.facts.services.syncthing.public.\"syncthing.pub\".value";
    };
    introducer = lib.mkOption {
      description = ''
        The introducer for the machine.
      '';
      type = lib.types.nullOr lib.types.str;
      default = null;
    };
    autoAcceptDevices = lib.mkOption {
      description = ''
        Auto accept incoming device requests.
        Should only be used on the introducer.
      '';
      type = lib.types.bool;
      default = false;
    };
    autoShares = lib.mkOption {
      description = ''
        Auto share the following Folders by their ID's with introduced devices.
        Should only be used on the introducer.
      '';
      type = lib.types.listOf lib.types.str;
      default = [ ];
      example = [
        "folder1"
        "folder2"
      ];
    };
  };

  imports = [
    {
      # Syncthing ports: 8384 for remote access to GUI
      # 22000 TCP and/or UDP for sync traffic
      # 21027/UDP for discovery
      # source: https://docs.syncthing.net/users/firewall.html
      networking.firewall.interfaces."zt+".allowedTCPPorts = [
        8384
        22000
      ];
      networking.firewall.allowedTCPPorts = [ 8384 ];
      networking.firewall.interfaces."zt+".allowedUDPPorts = [
        22000
        21027
      ];

      assertions = [
        {
          assertion = lib.all (
            attr: builtins.hasAttr attr config.services.syncthing.settings.folders
          ) config.clan.syncthing.autoShares;
          message = ''
            Syncthing: If you want to AutoShare a folder, you need to have it configured on the sharing device.
          '';
        }
      ];

      # Activates inotify compatibility on syncthing
      # use mkOverride 900 here as it otherwise would collide with the default of the
      # upstream nixos xserver.nix
      boot.kernel.sysctl."fs.inotify.max_user_watches" = lib.mkOverride 900 524288;

      services.syncthing = {
        enable = true;
        configDir = "/var/lib/syncthing";

        overrideFolders = lib.mkDefault (
          if (config.clan.syncthing.introducer == null) then true else false
        );
        overrideDevices = lib.mkDefault (
          if (config.clan.syncthing.introducer == null) then true else false
        );

        dataDir = lib.mkDefault "/home/user/";

        group = "syncthing";

        key = lib.mkDefault config.clan.secrets.syncthing.secrets."syncthing.key".path or null;
        cert = lib.mkDefault config.clan.secrets.syncthing.secrets."syncthing.cert".path or null;

        settings = {
          options = {
            urAccepted = -1;
            allowedNetworks = [ config.clan.core.networking.zerotier.subnet ];
          };
          devices =
            { }
            // (
              if (config.clan.syncthing.introducer == null) then
                { }
              else
                {
                  "${config.clan.syncthing.introducer}" = {
                    name = "introducer";
                    id = config.clan.syncthing.introducer;
                    introducer = true;
                    autoAcceptFolders = true;
                  };
                }
            );
        };
      };
      systemd.services.syncthing-auto-accept =
        let
          baseAddress = "127.0.0.1:8384";
          getPendingDevices = "/rest/cluster/pending/devices";
          postNewDevice = "/rest/config/devices";
          SharedFolderById = "/rest/config/folders/";
          apiKey = config.clan.core.facts.services.syncthing.secret."syncthing.api".path or null;
        in
        lib.mkIf config.clan.syncthing.autoAcceptDevices {
          description = "Syncthing auto accept devices";
          requisite = [ "syncthing.service" ];
          after = [ "syncthing.service" ];
          wantedBy = [ "multi-user.target" ];

          script = ''
            set -x
            # query pending deviceID's
            APIKEY=$(cat ${apiKey})
            PENDING=$(${lib.getExe pkgs.curl} -X GET -H "X-API-Key: $APIKEY" ${baseAddress}${getPendingDevices})
            PENDING=$(echo $PENDING | ${lib.getExe pkgs.jq} keys[])

            # accept pending deviceID's
            for ID in $PENDING;do
            ${lib.getExe pkgs.curl} -X POST -d "{\"deviceId\": $ID}" -H "Content-Type: application/json" -H "X-API-Key: $APIKEY" ${baseAddress}${postNewDevice}

            # get all shared folders by their ID
            for folder in ${builtins.toString config.clan.syncthing.autoShares}; do
              SHARED_IDS=$(${lib.getExe pkgs.curl} -X GET -H "X-API-Key: $APIKEY" ${baseAddress}${SharedFolderById}"$folder" | ${lib.getExe pkgs.jq} ."devices")
              PATCHED_IDS=$(echo $SHARED_IDS | ${lib.getExe pkgs.jq} ".+= [{\"deviceID\": $ID, \"introducedBy\": \"\", \"encryptionPassword\": \"\"}]")
              ${lib.getExe pkgs.curl} -X PATCH -d "{\"devices\": $PATCHED_IDS}" -H "X-API-Key: $APIKEY" ${baseAddress}${SharedFolderById}"$folder"
              done
            done
          '';
        };

      systemd.timers.syncthing-auto-accept = lib.mkIf config.clan.syncthing.autoAcceptDevices {
        description = "Syncthing Auto Accept";

        wantedBy = [ "syncthing-auto-accept.service" ];

        timerConfig = {
          OnActiveSec = lib.mkDefault 60;
          OnUnitActiveSec = lib.mkDefault 60;
        };
      };

      systemd.services.syncthing-init-api-key =
        let
          apiKey = config.clan.core.facts.services.syncthing.secret."syncthing.api".path or null;
        in
        lib.mkIf config.clan.syncthing.autoAcceptDevices {
          description = "Set the api key";
          after = [ "syncthing-init.service" ];
          wantedBy = [ "multi-user.target" ];
          script = ''
            # set -x
            set -efu pipefail

            APIKEY=$(cat ${apiKey})
            ${lib.getExe pkgs.gnused} -i "s/<apikey>.*<\/apikey>/<apikey>$APIKEY<\/apikey>/" /var/lib/syncthing/config.xml
            # sudo systemctl restart syncthing.service
            systemctl restart syncthing.service
          '';
          serviceConfig = {
            WorkingDirectory = "/var/lib/syncthing";
            BindReadOnlyPaths = [ apiKey ];
            Type = "oneshot";
          };
        };

      clan.core.facts.services.syncthing = {
        secret."syncthing.key" = { };
        secret."syncthing.cert" = { };
        secret."syncthing.api" = { };
        public."syncthing.pub" = { };
        generator.path = [
          pkgs.coreutils
          pkgs.gnugrep
          pkgs.syncthing
        ];
        generator.script = ''
          syncthing generate --config "$secrets"
          mv "$secrets"/key.pem "$secrets"/syncthing.key
          mv "$secrets"/cert.pem "$secrets"/syncthing.cert
          cat "$secrets"/config.xml | grep -oP '(?<=<device id=")[^"]+' | uniq > "$facts"/syncthing.pub
          cat "$secrets"/config.xml | grep -oP '<apikey>\K[^<]+' | uniq > "$secrets"/syncthing.api
        '';
      };
    }
  ];
}
