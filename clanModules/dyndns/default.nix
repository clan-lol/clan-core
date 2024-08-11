{
  config,
  pkgs,
  lib,
  ...
}:

let
  name = "dyndns";
  cfg = config.clan.${name};

  # We dedup secrets if they have the same provider + base domain
  secret_id = opt: "${name}-${opt.provider}-${opt.domain}";
  secret_path =
    opt: config.clan.core.facts.services."${secret_id opt}".secret."${secret_id opt}".path;

  /*
    We go from:
    {home.gchq.icu:{value:{domain:gchq.icu,host:home, provider:namecheap}}}
    To:
    {settings: [{domain: gchq.icu, host: home, provider: namecheap, password: dyndns-namecheap-gchq.icu}]}
  */
  service_config = {
    settings = builtins.catAttrs "value" (
      builtins.attrValues (
        lib.mapAttrs (_: opt: {
          value = opt // {
            password = secret_id opt;
          };
        }) cfg.settings
      )
    );
  };

  secret_generator = _: opt: {
    name = secret_id opt;
    value = {
      secret.${secret_id opt} = { };
      generator.prompt = "Dyndns passphrase for ${secret_id opt}";
      generator.script = ''
        echo "$prompt_value" > $secrets/${secret_id opt}
      '';
    };
  };
in
{
  options.clan.${name} = {

    user = lib.mkOption {
      type = lib.types.str;
      default = name;
      description = "User to run the service as";
    };
    group = lib.mkOption {
      type = lib.types.str;
      default = name;
      description = "Group to run the service as";
    };

    settings = lib.mkOption {
      type = lib.types.attrsOf (
        lib.types.submodule (
          { ... }:
          {
            options = {
              provider = lib.mkOption {
                type = lib.types.str;
                description = "The dyndns provider to use";
              };
              domain = lib.mkOption {
                type = lib.types.str;
                description = "The top level domain to update. For example 'example.com'.
              If you want to update a subdomain, add the 'subdomain' option";
              };
              host = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                description = "The subdomain to update of the tld";
              };
            };
          }
        )
      );
      default = [ ];
      description = "Wifi networks to predefine";
    };
  };

  imports = [
    (lib.mkRemovedOptionModule [
      "clan"
      "dyndns"
      "enable"
    ] "Just define clan.dyndns.settings to enable it")
  ];

  config = lib.mkMerge [
    (lib.mkIf (cfg.settings != { }) {
      clan.core.facts.services = lib.mapAttrs' secret_generator cfg.settings;

      users.groups.${cfg.group} = { };
      users.users.${cfg.user} = {
        group = cfg.group;
        isSystemUser = true;
        description = "User for ${name} service";
        home = "/var/lib/${name}";
        createHome = true;
      };

      systemd.services.${name} = {
        path = [ ];
        description = "Dynamic DNS updater";
        after = [ "network.target" ];
        wantedBy = [ "multi-user.target" ];
        environment = {
          MYCONFIG = "${builtins.toJSON service_config}";
        };

        serviceConfig =
          let
            pyscript = pkgs.writers.writePyPy3Bin "test.py" { libraries = [ ]; } ''
              import json
              from pathlib import Path
              import os

              cred_dir = Path(os.getenv("CREDENTIALS_DIRECTORY"))
              config_str = os.getenv("MYCONFIG")


              def get_credential(name):
                  secret_p = cred_dir / name
                  with open(secret_p, 'r') as f:
                      return f.read().strip()


              config = json.loads(config_str)
              print(f"Config: {config}")
              for attrset in config["settings"]:
                  attrset['password'] = get_credential(attrset['password'])

              # create directory data if it does not exist
              data_dir = Path('data')
              data_dir.mkdir(mode=0o770, exist_ok=True)

              # Write the config with secrets back
              config_path = data_dir / 'config.json'
              with open(config_path, 'w') as f:
                  f.write(json.dumps(config, indent=4))

              # Set file permissions to read and write
              # only by the user and group
              config_path.chmod(0o660)

              # Set file permissions to read
              # and write only by the user and group
              for file in data_dir.iterdir():
                  file.chmod(0o660)
            '';
          in
          {
            ExecStartPre = lib.getExe pyscript;
            ExecStart = lib.getExe pkgs.ddns-updater;
            LoadCredential = lib.mapAttrsToList (_: opt: "${secret_id opt}:${secret_path opt}") cfg.settings;
            User = cfg.user;
            Group = cfg.group;
            WorkingDirectory = "/var/lib/${name}";

            Restart = "always";
            RestartSec = 60;
          };
      };
    })
  ];
}
