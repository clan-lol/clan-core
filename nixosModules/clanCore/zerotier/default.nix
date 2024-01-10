{ config, lib, pkgs, ... }:
let
  cfg = config.clan.networking.zerotier;
  facts = config.clanCore.secrets.zerotier.facts or { };
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
    subnet = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      readOnly = true;
      default =
        if cfg.networkId == null then
          null
        else
          let
            part0 = builtins.substring 0 2 cfg.networkId;
            part1 = builtins.substring 2 2 cfg.networkId;
            part2 = builtins.substring 4 2 cfg.networkId;
            part3 = builtins.substring 6 2 cfg.networkId;
            part4 = builtins.substring 8 2 cfg.networkId;
            part5 = builtins.substring 10 2 cfg.networkId;
            part6 = builtins.substring 12 2 cfg.networkId;
            part7 = builtins.substring 14 2 cfg.networkId;
          in
          "fd${part0}:${part1}${part2}:${part3}${part4}:${part5}${part6}:${part7}99:9300::/88";
      description = ''
        zerotier subnet
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
    ({
      # Override license so that we can build zerotierone without
      # having to re-import nixpkgs.
      services.zerotierone.package = lib.mkDefault (pkgs.zerotierone.overrideAttrs (_old: { meta = { }; }));
    })
    (lib.mkIf ((facts.zerotier-meshname.value or null) != null) {
      environment.etc."zerotier/hostname".text = "${facts.zerotier-meshname.value}.vpn";
    })
    (lib.mkIf ((facts.zerotier-ip.value or null) != null) {
      environment.etc."zerotier/ip".text = facts.zerotier-ip.value;
    })
    (lib.mkIf (cfg.networkId != null) {
      clan.networking.meshnamed.networks.vpn.subnet = cfg.subnet;

      systemd.network.networks."09-zerotier" = {
        matchConfig.Name = "zt*";
        networkConfig = {
          LLMNR = true;
          LLDP = true;
          MulticastDNS = true;
          KeepConfiguration = "static";
        };
      };

      systemd.services.zerotierone.serviceConfig.ExecStartPre = [
        "+${pkgs.writeShellScript "init-zerotier" ''
           cp ${config.clanCore.secrets.zerotier.secrets.zerotier-identity-secret.path} /var/lib/zerotier-one/identity.secret

           ${lib.optionalString (cfg.controller.enable) ''
             mkdir -p /var/lib/zerotier-one/controller.d/network
             ln -sfT ${pkgs.writeText "net.json" (builtins.toJSON networkConfig)} /var/lib/zerotier-one/controller.d/network/${cfg.networkId}.json
           ''}
         ''}"
      ];

      networking.firewall.interfaces."zt+".allowedTCPPorts = [ 5353 ]; # mdns
      networking.firewall.interfaces."zt+".allowedUDPPorts = [ 5353 ]; # mdns

      networking.firewall.allowedTCPPorts = [ 9993 ]; # zerotier
      networking.firewall.allowedUDPPorts = [ 9993 ]; # zerotier

      networking.networkmanager.unmanaged = [ "interface-name:zt*" ];

      services.zerotierone = {
        enable = true;
        joinNetworks = [ cfg.networkId ];
      };
    })
    (lib.mkIf cfg.controller.enable {
      # only the controller needs to have the key in the repo, the other clients can be dynamic
      # we generate the zerotier code manually for the controller, since it's part of the bootstrap command
      clanCore.secrets.zerotier = {
        facts.zerotier-ip = { };
        facts.zerotier-meshname = { };
        facts.zerotier-network-id = { };
        secrets.zerotier-identity-secret = { };
        generator.path = [ config.services.zerotierone.package pkgs.fakeroot pkgs.python3 ];
        generator.script = ''
          python3 ${./generate.py} --mode network \
            --ip "$facts/zerotier-ip" \
            --meshname "$facts/zerotier-meshname" \
            --identity-secret "$secrets/zerotier-identity-secret" \
            --network-id "$facts/zerotier-network-id"
        '';
      };
      clanCore.state.zerotier.folders = [ "/var/lib/zerotier-one" ];

      environment.systemPackages = [ config.clanCore.clanPkgs.zerotier-members ];
    })
    (lib.mkIf (config.clanCore.secretsUploadDirectory != null && !cfg.controller.enable && cfg.networkId != null) {

      clanCore.secrets.zerotier = {
        facts.zerotier-ip = { };
        facts.zerotier-meshname = { };
        secrets.zerotier-identity-secret = { };
        generator.path = [ config.services.zerotierone.package pkgs.python3 ];
        generator.script = ''
          python3 ${./generate.py} --mode identity \
            --ip "$facts/zerotier-ip" \
            --meshname "$facts/zerotier-meshname" \
            --identity-secret "$secrets/zerotier-identity-secret" \
            --network-id ${cfg.networkId}
        '';
      };
    })
    (lib.mkIf (cfg.controller.enable && (facts.zerotier-network-id.value or null) != null) {
      clan.networking.zerotier.networkId = facts.zerotier-network-id.value;
      environment.etc."zerotier/network-id".text = facts.zerotier-network-id.value;
      systemd.services.zerotierone.serviceConfig.ExecStartPost = [
        "+${pkgs.writeShellScript "whitelist-controller" ''
          ${config.clanCore.clanPkgs.zerotier-members}/bin/zerotier-members allow ${builtins.substring 0 10 cfg.networkId}
        ''}"
      ];
    })
  ];
}
