{
  roles.telegraf.perInstance =
    { settings, ... }:
    {

      nixosModule =
        {
          config,
          pkgs,
          lib,
          ...
        }:
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

          clan.core.vars.generators."telegraf-password" = {
            files.telegraf-password.neededFor = "users";
            files.telegraf-password.restartUnits = [ "telegraf.service" ];

            runtimeInputs = [
              pkgs.coreutils
              pkgs.xkcdpass
              pkgs.mkpasswd
            ];

            script = ''
              PASSWORD=$(xkcdpass --numwords 4 --delimiter - --count 1 | tr -d "\n")
              echo "BASIC_AUTH_PWD=$PASSWORD" > "$out"/telegraf-password
            '';
          };

          services.telegraf = {
            enable = true;
            environmentFiles = [
              (builtins.toString
                config.clan.core.vars.generators."telegraf-password".files.telegraf-password.path
              )
            ];
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
                basic_username = "prometheus";
                basic_password = "$${BASIC_AUTH_PWD}";
              };
            };
          };
        };
    };
}
