{ config, lib, pkgs, ... }:
let
  secretsDir = config.clanCore.clanDir + "/sops/secrets";
  groupsDir = config.clanCore.clanDir + "/sops/groups";


  # My symlink is in the nixos module detected as a directory also it works in the repl. Is this because of pure evaluation?
  containsSymlink = path:
    builtins.pathExists path && (builtins.readFileType path == "directory" || builtins.readFileType path == "symlink");

  containsMachine = parent: name: type:
    type == "directory" && containsSymlink "${parent}/${name}/machines/${config.clanCore.machineName}";

  containsMachineOrGroups = name: type:
    (containsMachine secretsDir name type) || lib.any (group: type == "directory" && containsSymlink "${secretsDir}/${name}/groups/${group}") groups;

  filterDir = filter: dir:
    lib.optionalAttrs (builtins.pathExists dir)
      (lib.filterAttrs filter (builtins.readDir dir));

  groups = builtins.attrNames (filterDir (containsMachine groupsDir) groupsDir);
  secrets = filterDir containsMachineOrGroups secretsDir;
in
{
  config = lib.mkIf (config.clanCore.secretStore == "sops") {
    clanCore.secretsDirectory = "/run/secrets";
    clanCore.secretsPrefix = config.clanCore.machineName + "-";
    system.clan = lib.mkIf (config.clanCore.secrets != { }) {

      secretsModule = pkgs.writeText "sops.py" ''
        from pathlib import Path

        from clan_cli.secrets.folders import sops_secrets_folder
        from clan_cli.secrets.secrets import decrypt_secret, encrypt_secret, has_secret
        from clan_cli.secrets.sops import generate_private_key
        from clan_cli.secrets.machines import has_machine, add_machine
        from clan_cli.machines.machines import Machine


        class SecretStore:
            def __init__(self, machine: Machine) -> None:
                self.machine = machine
                if has_machine(self.machine.flake_dir, self.machine.name):
                    return
                priv_key, pub_key = generate_private_key()
                encrypt_secret(
                    self.machine.flake_dir,
                    sops_secrets_folder(self.machine.flake_dir) / f"{self.machine.name}-age.key",
                    priv_key,
                )
                add_machine(self.machine.flake_dir, self.machine.name, pub_key, False)

            def set(self, service: str, name: str, value: str):
                encrypt_secret(
                    self.machine.flake_dir,
                    sops_secrets_folder(self.machine.flake_dir) / f"{self.machine.name}-{name}",
                    value,
                    add_machines=[self.machine.name],
                )

            def get(self, service: str, name: str) -> bytes:
                # TODO: add support for getting a secret
                pass

            def exists(self, service: str, name: str) -> bool:
                return has_secret(
                    self.machine.flake_dir,
                    f"{self.machine.name}-{name}",
                )

            def upload(self, output_dir: Path, secrets: list[str, str]) -> None:
                key_name = f"{self.machine.name}-age.key"
                if not has_secret(self.machine.flake_dir, key_name):
                    # skip uploading the secret, not managed by us
                    return
                key = decrypt_secret(self.machine.flake_dir, key_name)

                (output_dir / "key.txt").write_text(key)
      '';
    };
    sops.secrets = builtins.mapAttrs
      (name: _: {
        sopsFile = config.clanCore.clanDir + "/sops/secrets/${name}/secret";
        format = "binary";
      })
      secrets;
    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    sops.defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" "")));

    sops.age.keyFile = lib.mkIf (builtins.pathExists (config.clanCore.clanDir + "/sops/secrets/${config.clanCore.machineName}-age.key/secret"))
      (lib.mkDefault "/var/lib/sops-nix/key.txt");
    clanCore.secretsUploadDirectory = lib.mkDefault "/var/lib/sops-nix";
  };
}
