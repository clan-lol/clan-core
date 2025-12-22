{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.core.networking.zerotier;
in
{
  options.clan.core.networking.zerotier = {
    networkId = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = ''
        zerotier networking id
      '';
    };
    name = lib.mkOption {
      type = lib.types.str;
      default = config.clan.core.settings.name;
      defaultText = "config.clan.core.name";
      description = ''
        zerotier network name
      '';
    };
    moon = {
      stableEndpoints = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
        description = ''
          Make this machine a moon.
          Other machines can join this moon by adding this moon in their config.
          It will be reachable under the given stable endpoints.
        '';
        example = ''
          [ 1.2.3.4" "10.0.0.3/9993" "2001:abcd:abcd::3/9993" ]
        '';
      };
      orbitMoons = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
        description = ''
          Join these moons.
          This machine will be able to reach all machines in these moons.
        '';
      };
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
      memberIps = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
        description = ''
          IPv6 addresses to authorize in controller.json when using the mesh controller.
        '';
      };
    };
    settings = lib.mkOption {
      description = "override the network config in /var/lib/zerotier/bla/$network.json";
      type = lib.types.submodule { freeformType = (pkgs.formats.json { }).type; };
    };
  };
  config = lib.mkMerge [
    {
      services.zerotierone.package = lib.mkDefault (
        pkgs.symlinkJoin {
          name = "mesh-controller-zerotier";
          paths = [ config.clan.core.clanPkgs.mesh-controller ];
          postBuild = ''
            ln -sf $out/bin/meshd $out/bin/zerotier-one
            ln -sf $out/bin/mesh-cli $out/bin/zerotier-cli
            ln -sf $out/bin/mesh-idtool $out/bin/zerotier-idtool
          '';
        }
      );
    }
    (lib.mkIf (cfg.networkId != null) {
      environment.etc."zerotier/ip".text =
        config.clan.core.vars.generators.zerotier.files.zerotier-ip.value;

      systemd.network.networks."09-zerotier" = {
        matchConfig.Name = "zt*";
        networkConfig = {
          LLDP = true;
          MulticastDNS = true;
          KeepConfiguration = "static";
        };
      };

      systemd.services.zerotierone.serviceConfig.ExecStartPre = [
        "+${pkgs.writeShellScript "init-zerotier" ''
          # compare hashes of the current identity secret and the one in the config
          hash1=$(sha256sum /var/lib/zerotier-one/identity.secret | cut -d ' ' -f 1)
          hash2=$(sha256sum ${config.clan.core.vars.generators.zerotier.files.zerotier-identity-secret.path} | cut -d ' ' -f 1)
          if [[ "$hash1" != "$hash2" ]]; then
            echo "Identity secret has changed, backing up old identity to /var/lib/zerotier-one/identity.secret.bac"
            cp /var/lib/zerotier-one/identity.secret /var/lib/zerotier-one/identity.secret.bac
            cp /var/lib/zerotier-one/identity.public /var/lib/zerotier-one/identity.public.bac
            cp ${config.clan.core.vars.generators.zerotier.files.zerotier-identity-secret.path} /var/lib/zerotier-one/identity.secret
            zerotier-idtool getpublic /var/lib/zerotier-one/identity.secret > /var/lib/zerotier-one/identity.public
          fi

          ${lib.optionalString (cfg.controller.enable) ''
            mkdir -p /var/lib/zerotier-one/controller.d/network
            ln -sfT ${pkgs.writeText "net.json" (builtins.toJSON cfg.settings)} /var/lib/zerotier-one/controller.d/network/${cfg.networkId}.json
          ''}
          ${lib.optionalString (cfg.moon.stableEndpoints != [ ]) ''
            if [[ ! -f /var/lib/zerotier-one/moon.json ]]; then
              zerotier-idtool initmoon /var/lib/zerotier-one/identity.public > /var/lib/zerotier-one/moon.json
            fi
            ${
              pkgs.runCommand "genmoon" { nativeBuildInputs = [ pkgs.python3 ]; } ''
                install -Dm755 ${./genmoon.py} $out/bin/genmoon
                patchShebangs $out/bin/genmoon
              ''
            }/bin/genmoon /var/lib/zerotier-one/moon.json ${builtins.toFile "moon.json" (builtins.toJSON cfg.moon.stableEndpoints)} /var/lib/zerotier-one/moons.d
          ''}

          # cleanup old networks
          if [[ -d /var/lib/zerotier-one/networks.d ]]; then
            find /var/lib/zerotier-one/networks.d \
              -type f \
              -name "*.conf" \
              -not \( ${
                lib.concatMapStringsSep " -o " (
                  netId: ''-name "${netId}.conf"''
                ) config.services.zerotierone.joinNetworks
              } \) \
              -delete
          fi
        ''}"
      ];
      systemd.services.zerotierone.serviceConfig.ExecStartPost = [
        "+${pkgs.writeShellScript "configure-interface" ''
          while ! ${pkgs.netcat}/bin/nc -z localhost 9993; do
            sleep 0.1
          done
          zerotier-cli listnetworks -j | ${pkgs.jq}/bin/jq -r '.[] | [.portDeviceName, .name] | @tsv' \
            | while IFS=$'\t' read -r portDeviceName name; do
              if [[ -z "$name" ]] || [[ -z "$portDeviceName" ]]; then
                continue
              fi
              # Execute the command for each element
              ${pkgs.iproute2}/bin/ip link property add dev "$portDeviceName" altname "$name"
          done

          ${lib.concatMapStringsSep "\n" (moon: ''
            zerotier-cli orbit ${moon} ${moon}
          '') cfg.moon.orbitMoons}
        ''}"
      ];

      networking.firewall.allowedTCPPorts = [ 9993 ]; # zerotier
      networking.firewall.allowedUDPPorts = [ 9993 ]; # zerotier

      networking.networkmanager.unmanaged = [ "interface-name:zt*" ];

      services.zerotierone = {
        enable = true;
        joinNetworks = [ cfg.networkId ];
      };

      systemd.services.zerotierone.serviceConfig = {
        StateDirectory = lib.mkForce "zerotier-one";
        WorkingDirectory = lib.mkForce "/var/lib/zerotier-one";
      };

      # The official zerotier tcp relay no longer works: https://github.com/zerotier/ZeroTierOne/issues/2202
      # So we host our own relay in https://git.clan.lol/clan/clan-infra
      services.zerotierone.localConf.settings.tcpFallbackRelay = "65.21.12.51/4443";
    })
    (lib.mkIf cfg.controller.enable {
      environment.etc."zerotier/ip".text =
        config.clan.core.vars.generators.zerotier.files.zerotier-ip.value;

      # only the controller needs to have the key in the repo, the other clients can be dynamic
      # we generate the zerotier code manually for the controller, since it's part of the bootstrap command
      clan.core.vars.generators.zerotier = {
        files.zerotier-ip.secret = false;
        files.zerotier-ip.restartUnits = [ "zerotierone.service" ];
        files.zerotier-network-id.secret = false;
        files.zerotier-network-id.restartUnits = [ "zerotierone.service" ];
        files.zerotier-identity-secret = {
          restartUnits = [ "zerotierone.service" ];
        };
        runtimeInputs = [
          config.services.zerotierone.package
          pkgs.python3
        ];
        script = ''
          source ${(pkgs.callPackage ../../../pkgs/minifakeroot { })}/share/minifakeroot/rc
          python3 ${./generate.py} --mode network \
            --ip "$out/zerotier-ip" \
            --identity-secret "$out/zerotier-identity-secret" \
            --network-id "$out/zerotier-network-id"
        '';
      };
      clan.core.state.zerotier.folders = [ "/var/lib/zerotier-one" ];
    })
    (lib.mkIf (!cfg.controller.enable && cfg.networkId != null) {
      clan.core.vars.generators.zerotier = {
        files.zerotier-ip.secret = false;
        files.zerotier-ip.restartUnits = [ "zerotierone.service" ];
        files.zerotier-identity-secret = {
          restartUnits = [ "zerotierone.service" ];
        };
        runtimeInputs = [
          config.services.zerotierone.package
          pkgs.python3
        ];
        script = ''
          python3 ${./generate.py} --mode identity \
            --ip "$out/zerotier-ip" \
            --identity-secret "$out/zerotier-identity-secret" \
            --network-id ${cfg.networkId}
        '';
      };
    })
    (lib.mkIf
      (!cfg.controller.enable && cfg.networkId != null && config.clan.core.vars.generators ? zerotier)
      {
        clan.core.networking.targetHost = lib.mkDefault "root@[${config.clan.core.vars.generators.zerotier.files.zerotier-ip.value}]";
      }
    )
    (lib.mkIf (cfg.controller.enable && config.clan.core.vars.generators ? zerotier) {
      clan.core.networking.zerotier.networkId =
        config.clan.core.vars.generators.zerotier.files.zerotier-network-id.value;
      clan.core.networking.zerotier.settings = {
        authTokens = [ null ];
        authorizationEndpoint = "";
        capabilities = [ ];
        clientId = "";
        dns = { };
        enableBroadcast = true;
        id = cfg.networkId;
        ipAssignmentPools = [ ];
        mtu = 2800;
        multicastLimit = 32;
        name = cfg.name;
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
            "or" = false;
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
      environment.etc."zerotier/network-id".text =
        config.clan.core.vars.generators.zerotier.files.zerotier-network-id.value;
    })
    (lib.mkIf (cfg.controller.enable && cfg.networkId != null) (
      let
        memberIps = lib.unique (
          cfg.controller.memberIps
          ++ lib.optional (
            config.clan.core.vars.generators ? zerotier
          ) config.clan.core.vars.generators.zerotier.files.zerotier-ip.value
        );
        controllerJson =
          pkgs.runCommand "zerotier-controller.json" { nativeBuildInputs = [ pkgs.python3 ]; }
            ''
              python3 - <<'PY'
              import ipaddress
              import json
              import os

              member_ips = json.loads(${builtins.toJSON (builtins.toJSON memberIps)})
              network_id = "${cfg.networkId}"
              members = []
              for ip in member_ips:
                  try:
                      addr = ipaddress.IPv6Address(ip)
                  except ValueError:
                      continue
                  node_id = int.from_bytes(addr.packed[10:16], byteorder="big")
                  members.append(format(node_id, "x").zfill(10)[-10:])
              members = sorted(set(members))
              with open(os.environ["out"], "w", encoding="utf-8") as f:
                  json.dump({"networks": [{"id": network_id, "members": members}]}, f, indent=2)
              PY
            '';
      in
      {
        systemd.services.zerotierone.serviceConfig.ExecStartPre = lib.mkAfter [
          "+${pkgs.writeShellScript "install-controller-json" ''
            mkdir -p /var/lib/zerotier-one
            cp -f ${controllerJson} /var/lib/zerotier-one/controller.json
          ''}"
        ];
        systemd.services.zerotierone.reloadIfChanged = true;
        systemd.services.zerotierone.reload = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
      }
    ))
  ];
}
