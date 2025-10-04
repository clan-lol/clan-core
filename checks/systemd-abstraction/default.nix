{ self, pkgs, ... }:

let

  cli = self.packages.${pkgs.hostPlatform.system}.clan-cli-full;
in
{
  name = "systemd-abstraction";

  nodes = {
    peer1 = {

      users.users.text-user = {
        isNormalUser = true;
        linger = true;
        uid = 1000;
        extraGroups = [ "systemd-journal" ];
      };

      # Set environment variables for user systemd
      environment.extraInit = ''
        if [ "$(id -u)" = "1000" ]; then
          export XDG_RUNTIME_DIR="/run/user/1000"
          export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus"
        fi
      '';

      # Enable PAM for user systemd sessions
      security.pam.services.systemd-user = {
        startSession = true;
        # Workaround for containers - use pam_permit to avoid helper binary issues
        text = pkgs.lib.mkForce ''
          account required pam_permit.so
          session required pam_permit.so
          session required pam_env.so conffile=/etc/pam/environment readenv=0
          session required ${pkgs.systemd}/lib/security/pam_systemd.so
        '';
      };

      environment.systemPackages = [
        cli
        (cli.pythonRuntime.withPackages (
          ps: with ps; [
            pytest
            pytest-xdist
          ]
        ))
      ];
    };
  };

  testScript =
    { ... }:
    ''
      start_all()

      peer1.wait_for_unit("multi-user.target")
      peer1.wait_for_unit("user@1000.service")

      # Fix user journal permissions so text-user can read their own logs
      peer1.succeed("chown text-user:systemd-journal /var/log/journal/*/user-1000.journal*")
      peer1.succeed("chmod 640 /var/log/journal/*/user-1000.journal*")

      # Run tests as text-user (environment variables are set automatically)
      peer1.succeed("su - text-user -c 'pytest -s -n0 ${cli}/${cli.pythonRuntime.sitePackages}/clan_lib/service_runner'")
    '';
}
