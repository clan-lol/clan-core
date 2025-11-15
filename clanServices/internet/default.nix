{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/internet";
  manifest.description = "Part of the clan networking abstraction to define how to reach machines from outside the clan network over the internet, if defined has the highest priority";
  manifest.categories = [
    "System"
    "Network"
  ];
  manifest.readme = builtins.readFile ./README.md;
  roles.default = {
    description = "Placeholder role to apply the internet service";
    interface =
      { lib, ... }:
      {
        options = {
          host = lib.mkOption {
            type = lib.types.str;
            default = "";
            description = ''
              ip address or hostname (domain) of the machine
            '';
          };
          jumphosts = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
            description = ''
              optional list of jumphosts to use to connect to the machine
            '';
          };
        };
      };
    perInstance =
      {
        roles,
        lib,
        mkExports,
        settings,
        ...
      }:
      {
        exports = mkExports {
          peer = {
              host.plain = settings.host;
              SSHOptions = map (_x: "-J x") settings.jumphosts;
            };
          # networking = {
          #   # TODO add user space network support to clan-cli
          #   peers = lib.mapAttrs (_name: machine: {
          #     host.plain = machine.settings.host;
          #     SSHOptions = map (_x: "-J x") machine.settings.jumphosts;
          #   }) roles.default.machines;
          # };
        };
      };
  };
}
