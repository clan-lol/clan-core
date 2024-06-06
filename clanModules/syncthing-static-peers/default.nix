{
  lib,
  config,
  pkgs,
  ...
}:
let
  clanDir = config.clanCore.clanDir;
  machineDir = clanDir + "/machines/";
  syncthingPublicKeyPath = machines: machineDir + machines + "/facts/syncthing.pub";
  machinesFileSet = builtins.readDir machineDir;
  machines = lib.mapAttrsToList (name: _: name) machinesFileSet;
  syncthingPublicKeysUnchecked = builtins.map (
    machine:
    let
      fullPath = syncthingPublicKeyPath machine;
    in
    if builtins.pathExists fullPath then machine else null
  ) machines;
  syncthingPublicKeyMachines = lib.filter (machine: machine != null) syncthingPublicKeysUnchecked;
  devices = builtins.map (machine: {
    name = machine;
    value = {
      name = machine;
      id = (builtins.readFile (syncthingPublicKeyPath machine));
    };
  }) syncthingPublicKeyMachines;
in
{
  options.clan.static-syncthing-peers = {
    excludeMachines = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      example = [ config.clanCore.machineName ];
      default = [ ];
      description = ''
        Machines that should not be added.
      '';
    };
  };

  config.services.syncthing.settings.devices = (builtins.listToAttrs devices);

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

      # Activates inotify compatibility on syncthing
      # use mkOverride 900 here as it otherwise would collide with the default of the
      # upstream nixos xserver.nix
      boot.kernel.sysctl."fs.inotify.max_user_watches" = lib.mkOverride 900 524288;

      services.syncthing = {
        enable = true;
        configDir = "/var/lib/syncthing";
        group = "syncthing";

        key = lib.mkDefault config.clan.secrets.syncthing.secrets."syncthing.key".path or null;
        cert = lib.mkDefault config.clan.secrets.syncthing.secrets."syncthing.cert".path or null;
      };

      clanCore.facts.services.syncthing = {
        secret."syncthing.key" = { };
        secret."syncthing.cert" = { };
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
        '';
      };
    }
  ];
}
