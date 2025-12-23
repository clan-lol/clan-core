{ lib, ... }:
let
  inherit (lib)
    attrNames
    flip
    ;

  varsForInstance = instanceName: pkgs: {
    clan.core.vars.generators."ncps-${instanceName}" = {
      share = true;
      files.sign-key.secret = true;
      files.sign-key.deploy = false;
      files.pub-key.secret = false;
      script = ''
        ${pkgs.nix}/bin/nix-store --generate-binary-cache-key ${instanceName}-1 \
          $out/sign-key \
          $out/pub-key
      '';
    };
  };
in
{
  _class = "clan.service";
  manifest.name = "ncps";
  manifest.description = "Use the ncps proxy cache to serve the nix store between machines in your network";
  manifest.categories = [ "Utility" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.server = {
    description = "The ncps proxy binary cache server";

    interface.options = with lib; {
      caches = mkOption {
        type = types.listOf types.str;
        description = ''
          Binary caches to add as upstream to ncps.
        '';
        default = [
          "https://cache.nixos.org"
          "https://nix-community.cachix.org"
        ];
      };
      publicKeys = mkOption {

        type = lib.types.listOf lib.types.str;
        description = ''
          Public keys to add as upstream to ncps.
        '';
        default = [
          "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
          "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
        ];
      };
      dataPath = lib.mkOption {
        type = lib.types.str;
        default = "/var/lib/ncps";
        description = ''
          The local directory for storing configuration and cached store paths
        '';
      };

      port = lib.mkOption {
        type = lib.types.int;
        default = 8501;
        description = "The port on which to host the ncps server";
      };
    };

    perInstance =
      { settings, instanceName, ... }:
      {
        nixosModule =
          { config, pkgs, ... }:
          let
            ncps-var = "ncps-${instanceName}";
          in
          {
            imports = [
              (varsForInstance instanceName pkgs)
            ];

            clan.core.vars.generators."${ncps-var}-private" = {
              dependencies = [
                "${ncps-var}"
              ];
              files.sign-key.secret = true;
              script = ''
                cp $in/${ncps-var}/sign-key $out/sign-key
              '';
            };

            networking.firewall.allowedTCPPorts = [ settings.port ];

            services.ncps.enable = true;
            services.ncps.server.addr = ":${builtins.toString settings.port}";
            services.ncps.cache = {
              inherit (settings) dataPath;
              allowPutVerb = true;
              secretKeyPath = config.clan.core.vars.generators."${ncps-var}-private".files.sign-key.path;
              hostName = config.networking.hostName;
            };
            services.ncps.upstream = { inherit (settings) caches publicKeys; };
          };
      };
  };

  roles.client = {
    description = "Clients that are configured to use the ncps proxy binary cache";
    perInstance =
      {
        instanceName,
        roles,
        ...
      }:
      {
        nixosModule =
          { config, pkgs, ... }:
          {
            imports = [
              (varsForInstance instanceName pkgs)
            ];

            # trust and use the cache
            nix.settings.substituters =
              let
                domain = config.clan.core.settings.domain;
                dotDomain = if domain != null then ".${domain}" else "";
              in
              flip map (attrNames roles.server.machines) (
                machineName:
                "http://${machineName}${dotDomain}:${
                  builtins.toString roles.server.machines.${machineName}.settings.port
                }?priority=10"
              );
            nix.settings.trusted-public-keys = [
              config.clan.core.vars.generators."ncps-${instanceName}".files.pub-key.value
            ];
          };

      };
  };
}
