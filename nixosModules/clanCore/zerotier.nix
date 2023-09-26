{ config, lib, pkgs, ... }:
let
  cfg = config.clan.networking.zerotier;
  networkConfig = {
    authTokens = [
      null
    ];
    authorizationEndpoint = "";
    capabilities = [ ];
    clientId = "";
    dns = [ ];
    enableBroadcast = true;
    id = cfg.networkId;
    ipAssignmentPools = [ ];
    mtu = 2800;
    multicastLimit = 32;
    name = "";
    uwid = cfg.networkId;
    objtype = "network";
    private = !cfg.controller.public;
    remoteTraceLevel = 0;
    remoteTraceTarget = null;
    revision = 1;
    routes = [ ];
    rules = [
      {
        not = false;
        or = false;
        type = "ACTION_ACCEPT";
      }
    ];
    rulesSource = "";
    ssoEnabled = false;
    tags = [ ];
    v4AssignMode = {
      zt = false;
    };
    v6AssignMode = {
      "6plane" = false;
      rfc4193 = true;
      zt = false;
    };
  };
in
{
  options.clan.networking.zerotier = {
    networkId = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = ''
        zerotier networking id
      '';
    };
    controller = {
      enable = lib.mkEnableOption "turn this machine into the networkcontroller";
      public = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = ''
          everyone can join a public network without having the administrator to accept
        '';
      };
    };
  };
  config = lib.mkMerge [
    (lib.mkIf (cfg.networkId != null) {
      systemd.network.networks.zerotier = {
        matchConfig.Name = "zt*";
        networkConfig = {
          LLMNR = true;
          LLDP = true;
          MulticastDNS = true;
          KeepConfiguration = "static";
        };
      };
      networking.firewall.allowedUDPPorts = [ 9993 ];
      networking.firewall.interfaces."zt+".allowedTCPPorts = [ 5353 ];
      networking.firewall.interfaces."zt+".allowedUDPPorts = [ 5353 ];
      services.zerotierone = {
        enable = true;
        joinNetworks = [ cfg.networkId ];
      };
    })
    (lib.mkIf cfg.controller.enable {
      # only the controller needs to have the key in the repo, the other clients can be dynamic
      # we generate the zerotier code manually for the controller, since it's part of the bootstrap command
      clanCore.secrets.zerotier = {
        facts."zerotier.network.id" = { };
        secrets."zerotier.identity.secret" = { };
        generator = ''
          TMPDIR=$(mktemp -d)
          trap 'rm -rf "$TMPDIR"' EXIT
          ${config.clanCore.clanPkgs.clan-cli}/bin/clan zerotier --outpath "$TMPDIR"
          cp "$TMPDIR"/network.id "$facts"/zerotier.network.id
          cp "$TMPDIR"/identity.secret "$secrets"/zerotier.identity.secret
        '';
      };

      systemd.services.zerotierone.serviceConfig.ExecStartPre = [
        "+${pkgs.writeShellScript "init_zerotier" ''
          cp /etc/secrets/zerotier.identity.secret /var/lib/zerotier-one/identity.secret
          ln -sfT ${pkgs.writeText "net.json" (builtins.toJSON networkConfig)} /var/lib/zerotier-one/controller.d/network/${cfg.networkId}.json
        ''}"
      ];
    })
  ];
}

