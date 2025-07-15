{ config, ... }:
{
  systemd.services.dummy-service = {
    enable = true;
    description = "Dummy service";
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
    };
    script = ''
      generated_password_path="${config.clan.core.vars.generators.dummy-generator.files.generated-password.path}"
      if [ ! -f "$generated_password_path" ]; then
        echo "Generated password file not found: $generated_password_path"
        exit 1
      fi
      host_id_path="${config.clan.core.vars.generators.dummy-generator.files.host-id.path}"
      if [ ! -e "$host_id_path" ]; then
        echo "Host ID file not found: $host_id_path"
        exit 1
      fi
    '';
  };

  # TODO: add and prompt and make it work in the test framework
  clan.core.vars.generators.dummy-generator = {
    files.host-id.secret = false;
    files.generated-password.secret = true;
    script = ''
      echo $RANDOM > "$out"/host-id
      echo $RANDOM > "$out"/generated-password
    '';
  };
}
