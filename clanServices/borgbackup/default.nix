{ ... }:
{
  _class = "clan.service";
  manifest.name = "borgbackup";
  manifest.description = "Efficient, deduplicating backup program with optional compression and secure encryption.";
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  # TODO: a client can only be in one instance, add constraint

  roles.server = {

    interface =
      { lib, ... }:
      {

        options.directory = lib.mkOption {
          type = lib.types.str;
          default = "/var/lib/borgbackup";
          description = ''
            The directory where the borgbackup repositories are stored.
          '';
        };

      };

    perInstance =
      {
        roles,
        settings,
        ...
      }:
      {
        nixosModule =
          {
            config,
            ...
          }:
          {

            config.services.openssh.enable = true;

            config.services.borgbackup.repos =
              let
                borgbackupIpMachinePath =
                  machine:
                  config.clan.core.settings.directory
                  + "/vars/per-machine/${machine}/borgbackup/borgbackup.ssh.pub/value";

                hosts = builtins.mapAttrs (machineName: _machineSettings: {
                  # name = "${instanceName}-${machineName}";
                  # value = {
                  path = "${settings.directory}/${machineName}";
                  authorizedKeys = [ (builtins.readFile (borgbackupIpMachinePath machineName)) ];
                  # };
                  # }) machinesWithKey;
                }) (roles.client.machines or { });
              in
              hosts;
          };
      };
  };

  roles.client = {
    interface =
      {
        lib,
        ...
      }:
      {

        options.destinations = lib.mkOption {
          type = lib.types.attrsOf (
            lib.types.submodule (
              { name, ... }:
              {
                options = {
                  name = lib.mkOption {
                    type = lib.types.strMatching "^[a-zA-Z0-9._-]+$";
                    default = name;
                    description = "the name of the backup job";
                  };
                  repo = lib.mkOption {
                    type = lib.types.str;
                    description = "the borgbackup repository to backup to";
                  };
                  rsh = lib.mkOption {
                    type = lib.types.str;
                    defaultText = "ssh -i \${config.clan.core.vars.generators.borgbackup.files.\"borgbackup.ssh\".path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
                    description = "the rsh to use for the backup";
                  };
                };
              }
            )
          );
          default = { };
          description = ''
            external destinations where the machine should be backuped to
          '';
        };

        options.exclude = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          example = [ "*.pyc" ];
          default = [ ];
          description = ''
            Directories/Files to exclude from the backup.
            Use * as a wildcard.
          '';
        };
      };

    perInstance =
      {
        extendSettings,
        roles,
        ...
      }:
      {
        nixosModule =
          {
            config,
            lib,
            pkgs,
            ...
          }:
          let
            settings = extendSettings {

              # Adding default value with option merging, because it depends on
              # generators, which we can reference here.
              options.destinations = lib.mkOption {
                type = lib.types.attrsOf (
                  lib.types.submodule {
                    options = {
                      rsh = lib.mkOption {
                        default = "ssh -i ${
                          config.clan.core.vars.generators.borgbackup.files."borgbackup.ssh".path
                        } -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentitiesOnly=Yes -o PasswordAuthentication=no";
                      };
                    };
                  }
                );
              };
            };

          in

          {
            config =
              let
                preBackupScript = ''
                  declare -A preCommandErrors

                  ${lib.concatMapStringsSep "\n" (
                    state:
                    lib.optionalString (state.preBackupCommand != null) ''
                      echo "Running pre-backup command for ${state.name}"
                      if ! /run/current-system/sw/bin/${state.preBackupCommand}; then
                        preCommandErrors["${state.name}"]=1
                      fi
                    ''
                  ) (lib.attrValues config.clan.core.state)}

                  if [[ ''${#preCommandErrors[@]} -gt 0 ]]; then
                    echo "pre-backup commands failed for the following services:"
                    for state in "''${!preCommandErrors[@]}"; do
                      echo "  $state"
                    done
                    exit 1
                  fi
                '';

                # The destinations from server.roles.machines.*
                # name is the server, machine can only be in one instance
                internalDestinations =
                  let
                    destinations = builtins.map (serverName: {
                      name = "${serverName}";
                      value = {
                        # inherit name;
                        name = "${serverName}";
                        repo = "borg@${serverName}:.";
                        # rsh = "";

                        rsh = "ssh -i ${
                          config.clan.core.vars.generators.borgbackup.files."borgbackup.ssh".path
                        } -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentitiesOnly=Yes";
                      };
                    }) (builtins.attrNames (roles.server.machines or { }));
                  in
                  (builtins.listToAttrs destinations);

                # The destinations specified via roles.client.machines.*.settings.destinations.<name>
                # name is the <name>
                externalDestinations = lib.mapAttrs' (
                  name: dest: lib.nameValuePair name dest
                ) settings.destinations;

                allDestinations =
                  lib.warnIf ((builtins.intersectAttrs externalDestinations internalDestinations) != { })
                    "You are overwriting an internalDestinations through an externalDestination configuration."
                    (internalDestinations // externalDestinations);

              in
              {
                services.openssh.enable = true;

                # Derived from the destinations
                systemd.services = lib.mapAttrs' (
                  destName: _dest:
                  lib.nameValuePair "borgbackup-job-${destName}" {
                    # since borgbackup mounts the system read-only, we need to
                    # run in a ExecStartPre script, so we can generate
                    # additional files.
                    serviceConfig.ExecStartPre = [
                      ''+${pkgs.writeShellScript "borgbackup-job-${destName}-pre-backup-commands" preBackupScript}''
                    ];
                  }
                ) allDestinations;

                services.borgbackup.jobs = lib.mapAttrs (_: dest: {
                  paths = lib.unique (
                    lib.flatten (map (state: state.folders) (lib.attrValues config.clan.core.state))
                  );
                  exclude = settings.exclude;
                  repo = dest.repo;
                  environment.BORG_RSH = dest.rsh;
                  compression = "auto,zstd";
                  startAt = "*-*-* 01:00:00";
                  persistentTimer = true;

                  encryption = {
                    mode = "repokey";
                    passCommand = "cat ${config.clan.core.vars.generators.borgbackup.files."borgbackup.repokey".path}";
                  };

                  prune.keep = {
                    within = "1d"; # Keep all archives from the last day
                    daily = 7;
                    weekly = 4;
                    monthly = 0;
                  };
                }) allDestinations;

                clan.core.vars.generators.borgbackup = {

                  files."borgbackup.ssh.pub".secret = false;
                  files."borgbackup.ssh" = { };
                  files."borgbackup.repokey" = { };

                  migrateFact = "borgbackup";
                  runtimeInputs = [
                    pkgs.coreutils
                    pkgs.openssh
                    pkgs.xkcdpass
                  ];
                  script = ''
                    ssh-keygen -t ed25519 -N "" -C "" -f "$out"/borgbackup.ssh
                    xkcdpass -n 4 -d - > "$out"/borgbackup.repokey
                  '';
                };

                clan.core.backups.providers.borgbackup = {
                  list = "borgbackup-list";
                  create = "borgbackup-create";
                  restore = "borgbackup-restore";
                };

                environment.systemPackages = [
                  (pkgs.writeShellApplication {
                    name = "borgbackup-create";
                    runtimeInputs = [ config.systemd.package ];
                    text = ''
                      ${lib.concatMapStringsSep "\n" (dest: ''
                        systemctl start borgbackup-job-${dest}
                      '') (lib.attrNames allDestinations)}
                    '';
                  })
                  (pkgs.writeShellApplication {
                    name = "borgbackup-list";
                    runtimeInputs = [ pkgs.jq ];
                    text = ''
                      (${
                        lib.concatMapStringsSep "\n" (
                          dest:
                          # we need yes here to skip the changed url verification
                          ''echo y | /run/current-system/sw/bin/borg-job-${dest.name} list --json | jq '[.archives[] | {"name": ("${dest.name}::${dest.repo}::" + .name)}]' ''
                        ) (lib.attrValues allDestinations)
                      }) | jq -s 'add // []'
                    '';
                  })
                  (pkgs.writeShellApplication {
                    name = "borgbackup-restore";
                    runtimeInputs = [ pkgs.gawk ];
                    text = ''
                      cd /
                      IFS=':' read -ra FOLDER <<< "''${FOLDERS-}"
                      job_name=$(echo "$NAME" | awk -F'::' '{print $1}')
                      backup_name=''${NAME#"$job_name"::}
                      if [[ ! -x /run/current-system/sw/bin/borg-job-"$job_name" ]]; then
                        echo "borg-job-$job_name not found: Backup name is invalid" >&2
                        exit 1
                      fi
                      echo y | /run/current-system/sw/bin/borg-job-"$job_name" extract "$backup_name" "''${FOLDER[@]}"
                    '';
                  })
                ];
              };
          };
      };
  };
}
