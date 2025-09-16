{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/internet";
  manifest.description = "direct access (or via ssh jumphost) to machines";
  manifest.categories = [
    "System"
    "Network"
  ];
  roles.default = {
    interface =
      { lib, ... }:
      {
        options = {
          host = lib.mkOption {
            type = lib.types.str;
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
        ...
      }:
      {
        exports.networking = {
          # TODO add user space network support to clan-cli
          peers = lib.mapAttrs (_name: machine: {
            host.plain = machine.settings.host;
            SSHOptions = map (_x: "-J x") machine.settings.jumphosts;
          }) roles.default.machines;
        };
      };
  };
}
