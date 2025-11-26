{
  config,
  lib,
  pkgs,
  ...
}:

let
  cfg = config.clan.core.networking.extraHosts;
in
{
  options = {
    clan.core.networking.extraHosts = lib.mkOption {
      type = lib.types.attrsOf lib.types.lines;
      default = { };
      example = lib.literalExpression ''
        {
          wireguard = '''
            fd28:387a:2:b100::1 eva.x
            fd28:387a:85:2600::1 eve.x
          ''';
        }
      '';
      description = ''
        Additional hosts entries to add to /etc/hosts on darwin systems.
        Each attribute creates a separate section in the hosts file with
        delimiters, allowing multiple services to manage their entries
        independently.

        This uses launchd daemons to manage /etc/hosts since it cannot
        be a symlink on macOS.
      '';
    };
  };

  config = lib.mkIf (cfg != { }) {
    launchd.daemons = lib.mapAttrs' (
      name: hostsContent:
      lib.nameValuePair "hosts-update-${name}" (
        let
          sectionName = lib.toUpper name;
          updateHosts = pkgs.writeShellScript "update-hosts-${name}" ''
            # Hosts content for ${name}
            hosts_content=$(cat <<'EOF'
            ${hostsContent}
            EOF
            )

            # Check if /private/etc/hosts exists
            if [ ! -f /private/etc/hosts ]; then
              echo "Error: /private/etc/hosts not found"
              exit 1
            fi

            # Create a temporary file in /private/etc/
            temp_file=$(mktemp /private/etc/hosts.XXXXXX)

            # Set proper permissions for the temp file
            chmod 644 "$temp_file"

            # Check if ${name} section exists
            if grep -q "^# BEGIN ${sectionName} HOSTS$" /private/etc/hosts; then
              # Update existing section
              awk '
                BEGIN { in_section = 0 }
                /^# BEGIN ${sectionName} HOSTS$/ { in_section = 1; next }
                /^# END ${sectionName} HOSTS$/ { in_section = 0; next }
                !in_section { print }
              ' /private/etc/hosts > "$temp_file"

              # Add the ${name} section
              echo "# BEGIN ${sectionName} HOSTS" >> "$temp_file"
              echo "$hosts_content" >> "$temp_file"
              echo "# END ${sectionName} HOSTS" >> "$temp_file"

              # Copy everything after the section
              awk '
                BEGIN { in_section = 0; after_section = 0 }
                /^# BEGIN ${sectionName} HOSTS$/ { in_section = 1; next }
                /^# END ${sectionName} HOSTS$/ { in_section = 0; after_section = 1; next }
                after_section && !in_section { print }
              ' /private/etc/hosts >> "$temp_file"
            else
              # First time - append to existing hosts file
              cp /private/etc/hosts "$temp_file"
              echo "" >> "$temp_file"  # Ensure newline before our section
              echo "# BEGIN ${sectionName} HOSTS" >> "$temp_file"
              echo "$hosts_content" >> "$temp_file"
              echo "# END ${sectionName} HOSTS" >> "$temp_file"
            fi

            # Replace the hosts file (permissions already set on temp file)
            mv "$temp_file" /private/etc/hosts
          '';
        in
        {
          command = toString updateHosts;
          serviceConfig = {
            Label = "io.clan.hosts-update.${name}";
            RunAtLoad = true;
            StandardErrorPath = "/var/log/hosts-update-${name}.log";
            StandardOutPath = "/var/log/hosts-update-${name}.log";
          };
        }
      )
    ) cfg;
  };
}
