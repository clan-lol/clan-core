{
  lib,
  config,
  pkgs,
  ...
}:
let
  var = config.clan.core.vars.generators.machine-id.files.machineId or { };
in
{

  options.clan.core.settings.machine-id = {
    enable = lib.mkEnableOption ''
      machine ID generation. Sets the /etc/machine-id and exposes it as a nix
      option. This unique ID that is not dependent on ephemeral or
      variable data, such as hostnames, MAC addresses or IP addresses.

      See https://www.freedesktop.org/software/systemd/man/latest/machine-id.html for details.
    '';
  };

  config = lib.mkIf (config.clan.core.settings.machine-id.enable) {

    assertions = [
      {
        assertion = lib.stringLength var.value == 32;
        message = "machine ID must be exactly 32 characters long.";
      }
    ];

    boot.kernelParams = [
      ''systemd.machine_id=${var.value}''
    ];

    environment.etc."machine-id".text = var.value;

    clan.core.vars.generators.machine-id = {
      files.machineId.secret = false;
      runtimeInputs = [
        pkgs.coreutils
        pkgs.bash
      ];
      script = ''
        uuid=$(bash ${./uuid4.sh})

        # Remove the hyphens from the UUID
        uuid_no_hyphens=$(echo -n "$uuid" | tr -d '-')

        echo -n "$uuid_no_hyphens" > "$out/machineId"
      '';
    };
  };
}
