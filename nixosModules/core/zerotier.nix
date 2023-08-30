{ config, lib, pkgs, ... }:
let
  cfg = config.clan.networking.zerotier;
in
{
  options.clan.networking.zerotier = {
    networkId = lib.mkOption {
      type = lib.types.str;
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
  config = {
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
  } // lib.mkIf cfg.controller.enable {
    # only the controller needs to have the key in the repo, the other clients can be dynamic
    # we generate the zerotier code manually for the controller, since it's part of the bootstrap command
    clan.core.secrets.zerotier = {
      facts."network.id" = { };
      secrets."identity.secret" = { };
      generator = ''
        TMPDIR=$(mktemp -d)
        trap 'rm -rf "$TMPDIR"' EXIT
        ${config.clan.core.clanPkgs.clan-cli}/bin/clan zerotier --outpath "$TMPDIR"
        cp "$TMPDIR"/network.id "$facts"/network.id
        cp "$TMPDIR"/identity.secret "$secrets"/identity.secret
      '';
    };

    systemd.tmpfiles.rules = [
      "L+ /var/lib/zerotierone/controller.d/network/${cfg.networkId}.json - - - - ${pkgs.writeText "net.json" (builtins.toJSON {
        authTokens = [
          null
        ];
        authorizationEndpoint = "";
        capabilities = [];
        clientId = "";
        dns = [];
        enableBroadcast = true;
        id = cfg.networkId;
        ipAssignmentPools = [];
        mtu = 2800;
        multicastLimit = 32;
        name = "";
        uwid = cfg.networkId;
        objtype = "network";
        private = true;
        remoteTraceLevel = 0;
        remoteTraceTarget = null;
        revision = 1;
        routes = [];
        rules = [
          {
            not = false;
            or = false;
            type = "ACTION_ACCEPT";
          }
        ];
        rulesSource = "";
        ssoEnabled = false;
        tags = [];
        v4AssignMode = {
          zt = false;
        };
        v6AssignMode = {
          "6plane" = false;
          rfc4193 = false;
          zt = false;
        };
      })}"
    ];
  };
}

