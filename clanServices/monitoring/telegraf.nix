{
  roles.telegraf.perInstance =
    { settings, ... }:
    {

      nixosModule =
        { pkgs, lib, ... }:
        {

          networking.firewall.interfaces = lib.mkIf (settings.allowAllInterfaces == false) (
            builtins.listToAttrs (
              map (name: {
                inherit name;
                value.allowedTCPPorts = [ 9273 ];
              }) settings.interfaces
            )
          );

          networking.firewall.allowedTCPPorts = lib.mkIf (settings.allowAllInterfaces == true) [ 9273 ];

          services.telegraf = {
            enable = true;
            extraConfig = {
              agent.interval = "60s";
              inputs = {

                diskio = { };
                kernel_vmstat = { };
                system = { };
                mem = { };
                systemd_units = { };
                swap = { };

                exec =
                  let
                    currentSystemScript = pkgs.writeShellScript "current-system" ''
                      printf "current_system,path=%s present=0\n" $(readlink /run/current-system)
                    '';
                  in
                  [
                    {
                      # Expose the path to current-system as metric. We use
                      # this to check if the machine is up-to-date.
                      commands = [ currentSystemScript ];
                      data_format = "influx";
                    }
                  ];
              };
              outputs.prometheus_client = {
                listen = ":9273";
                metric_version = 2;
              };
            };
          };
        };
    };
}
