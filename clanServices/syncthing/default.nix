{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/syncthing";
  manifest.description = "Syncthing file synchronization with automatic peer discovery";
  manifest.categories = [ "File Sync" ];

  roles.peer = {
    interface =
      { lib, ... }:
      {
        options.openDefaultPorts = lib.mkOption {
          type = lib.types.bool;
          default = true;
          description = ''
            Whether to open the default syncthing ports in the firewall.
          '';
        };

        options.folders = lib.mkOption {
          type = lib.types.attrsOf (
            lib.types.submodule {
              options = {
                path = lib.mkOption {
                  type = lib.types.str;
                  description = "Path to the folder to sync";
                };
                devices = lib.mkOption {
                  type = lib.types.listOf lib.types.str;
                  default = [ ];
                  description = "List of device names to share this folder with. Empty list means all peers and extraDevices.";
                };
                ignorePerms = lib.mkOption {
                  type = lib.types.bool;
                  default = false;
                  description = "Ignore permission changes";
                };
                rescanIntervalS = lib.mkOption {
                  type = lib.types.int;
                  default = 3600;
                  description = "Rescan interval in seconds";
                };
                type = lib.mkOption {
                  type = lib.types.enum [
                    "sendreceive"
                    "sendonly"
                    "receiveonly"
                  ];
                  default = "sendreceive";
                  description = "Folder type";
                };
                versioning = lib.mkOption {
                  type = lib.types.nullOr (
                    lib.types.submodule {
                      options = {
                        type = lib.mkOption {
                          type = lib.types.enum [
                            "external"
                            "simple"
                            "staggered"
                            "trashcan"
                          ];
                          description = "Versioning type";
                        };
                        params = lib.mkOption {
                          type = lib.types.attrsOf lib.types.str;
                          default = { };
                          description = "Versioning parameters";
                        };
                      };
                    }
                  );
                  default = null;
                  description = "Versioning configuration";
                };
              };
            }
          );
          default = { };
          description = "Folders to synchronize between all peers";
        };

        options.extraDevices = lib.mkOption {
          type = lib.types.attrsOf (
            lib.types.submodule {
              options = {
                id = lib.mkOption {
                  type = lib.types.str;
                  description = "Device ID of the external syncthing device";
                  example = "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2";
                };
                addresses = lib.mkOption {
                  type = lib.types.listOf lib.types.str;
                  default = [ "dynamic" ];
                  description = "List of addresses for the device";
                  example = [
                    "dynamic"
                    "tcp://192.168.1.100:22000"
                  ];
                };
                name = lib.mkOption {
                  type = lib.types.str;
                  default = "";
                  description = "Human readable name for the device";
                };
              };
            }
          );
          default = { };
          description = "External syncthing devices not managed by clan (e.g., mobile phones)";
          example = lib.literalExpression ''
            {
              phone = {
                id = "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2";
                name = "My Phone";
                addresses = [ "dynamic" ];
              };
            }
          '';
        };
      };

    perInstance =
      {
        settings,
        roles,
        ...
      }:
      {
        nixosModule =
          {
            config,
            lib,
            ...
          }:
          let
            allPeerMachines = lib.attrNames roles.peer.machines;

            readMachineVar =
              machine: varPath: default:
              let
                fullPath = "${config.clan.core.settings.directory}/vars/per-machine/${machine}/${varPath}";
              in
              if builtins.pathExists fullPath then
                lib.removeSuffix "\n" (builtins.readFile fullPath)
              else
                default;

            peerDevices = lib.listToAttrs (
              lib.forEach allPeerMachines (machine: {
                name = machine;
                value = {
                  name = machine;
                  id = readMachineVar machine "syncthing/id/value" "";
                  addresses = [
                    "dynamic"
                  ]
                  ++
                    lib.optional (readMachineVar machine "zerotier/zerotier-ip/value" null != null)
                      "tcp://[${readMachineVar machine "zerotier/zerotier-ip/value" ""}]:22000";
                };
              })
            );

            extraDevicesConfig = lib.mapAttrs (deviceName: deviceConfig: {
              inherit (deviceConfig) id addresses;
              name = if deviceConfig.name != "" then deviceConfig.name else deviceName;
            }) settings.extraDevices;

            allDevices = peerDevices // extraDevicesConfig;

            validDevices = lib.filterAttrs (_: device: device.id != "") allDevices;

            syncthingFolders = lib.mapAttrs (
              _folderName: folderConfig:
              let
                targetDevices =
                  if folderConfig.devices == [ ] then lib.attrNames validDevices else folderConfig.devices;
              in
              folderConfig
              // {
                devices = targetDevices;
              }
            ) settings.folders;
          in
          {
            imports = [
              ./vars.nix
            ];

            config = lib.mkMerge [
              {
                services.syncthing = {
                  enable = true;
                  configDir = "/var/lib/syncthing";
                  group = "syncthing";

                  key = lib.mkDefault config.clan.core.vars.generators.syncthing.files.key.path or null;
                  cert = lib.mkDefault config.clan.core.vars.generators.syncthing.files.cert.path or null;

                  settings = {
                    devices = validDevices;
                    folders = syncthingFolders;
                  };
                };
              }

              # Conditionally open firewall ports
              (lib.mkIf settings.openDefaultPorts {
                services.syncthing.openDefaultPorts = true;
                # Syncthing ports: 8384 for remote access to GUI
                # 22000 TCP and/or UDP for sync traffic
                # 21027/UDP for discovery
                # source: https://docs.syncthing.net/users/firewall.html
                networking.firewall.interfaces."zt+".allowedTCPPorts = [
                  8384
                  22000
                ];
                networking.firewall.interfaces."zt+".allowedUDPPorts = [
                  22000
                  21027
                ];
              })
            ];
          };
      };
  };
  perMachine = _: {
    nixosModule =
      { lib, ... }:
      {
        # Activates inotify compatibility on syncthing
        # use mkOverride 900 here as it otherwise would collide with the default of the
        # upstream nixos xserver.nix
        boot.kernel.sysctl."fs.inotify.max_user_watches" = lib.mkOverride 900 524288;
      };
  };
}
