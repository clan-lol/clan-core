{ self, pkgs, ... }:

let

  cli = self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full;

  ollama-model = pkgs.callPackage ./qwen3-4b-instruct.nix { };
in
{
  name = "llm";

  nodes = {
    peer1 =
      { pkgs, ... }:
      {

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

            ollama_dir="$HOME/.ollama"
            mkdir -p "$ollama_dir"
            ln -sf ${ollama-model}/models "$ollama_dir"/models
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
          pkgs.ollama
          (cli.pythonRuntime.withPackages (
            ps: with ps; [
              pytest
              pytest-xdist
              (cli.pythonRuntime.pkgs.toPythonModule cli)
              self.legacyPackages.${pkgs.stdenv.hostPlatform.system}.nixosTestLib
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
      # the -o adopts="" is needed to overwrite any args coming from pyproject.toml
      # -p no:cacheprovider disables pytest's cacheprovider which tries to write to the nix store in this case
      cmd = "su - text-user -c 'pytest -s -n0 -m service_runner -p no:cacheprovider -o addopts="" ${cli.passthru.sourceWithTests}/clan_lib/llm'"
      print("Running tests with command: " + cmd)

      # Run tests as text-user (environment variables are set automatically)
      peer1.succeed(cmd)
    '';
}
