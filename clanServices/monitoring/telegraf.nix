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
        let
          auth_user = "prometheus";
        in
        {

          networking.firewall.interfaces = lib.mkIf (settings.allowAllInterfaces == false) (
            builtins.listToAttrs (
              map (name: {
                inherit name;
                value.allowedTCPPorts = [
                  9273
                  9990
                ];
              }) settings.interfaces
            )
          );

          networking.firewall.allowedTCPPorts = lib.mkIf (settings.allowAllInterfaces == true) [
            9273
            9990
          ];

          clan.core.vars.generators."telegraf" = {

            files.password.restartUnits = [ "telegraf.service" ];
            files.password-env.restartUnits = [ "telegraf.service" ];
            files.miniserve-auth.restartUnits = [ "telegraf.service" ];

            runtimeInputs = [
              pkgs.coreutils
              pkgs.xkcdpass
              pkgs.mkpasswd
            ];

            script = ''
              PASSWORD=$(xkcdpass --numwords 4 --delimiter - --count 1 | tr -d "\n")
              echo "BASIC_AUTH_PWD=$PASSWORD" > "$out"/password-env
              echo "${auth_user}:$PASSWORD" > "$out"/miniserve-auth
              echo "$PASSWORD" | tr -d "\n" > "$out"/password
            '';
          };

          systemd.services.telegraf-json = {
            enable = true;
            wantedBy = [ "multi-user.target" ];
            after = [ "telegraf.service" ];
            wants = [ "telegraf.service" ];
            serviceConfig = {
              LoadCredential = [
                "auth_file_path:${config.clan.core.vars.generators.telegraf.files.miniserve-auth.path}"
              ];
              Environment = [
                "AUTH_FILE_PATH=%d/auth_file_path"
              ];
              Restart = "on-failure";
              User = "telegraf";
              Group = "telegraf";
            };
            script = "${pkgs.miniserve}/bin/miniserve -p 9990 /var/lib/telegraf/telegraf.json --auth-file \"$AUTH_FILE_PATH\"";
          };

          users.users.telegraf = {
            home = "/var/lib/telegraf";
            createHome = true;
          };

          services.telegraf = {
            enable = true;
            environmentFiles = [
              (builtins.toString config.clan.core.vars.generators.telegraf.files.password-env.path)
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
                    nixosSystems = pkgs.writeShellScript "current-system" ''
                      printf "nixos_systems,current_system=%s,booted_system=%s,current_kernel=%s,booted_kernel=%s present=0\n" \
                        "$(readlink /run/current-system)" "$(readlink /run/booted-system)" \
                        "$(basename $(echo /run/current-system/kernel-modules/lib/modules/*))" \
                        "$(basename $(echo /run/booted-system/kernel-modules/lib/modules/*))"
                    '';
                  in
                  [
                    {
                      # Expose the path to current-system as metric. We use
                      # this to check if the machine is up-to-date.
                      commands = [ nixosSystems ];
                      data_format = "influx";
                    }
                  ];
              };
              # sadly there doesn'T seem to exist a telegraf http_client output plugin
              outputs.prometheus_client = {
                listen = ":9273";
                metric_version = 2;
                basic_username = "${auth_user}";
                basic_password = "$${BASIC_AUTH_PWD}";
              };

              outputs.file = {
                files = [ "/var/lib/telegraf/telegraf.json" ];
                data_format = "json";
                json_timestamp_units = "1s";
              };
            };
          };
        };
    };
}
