{ config, lib, pkgs, ... }:
{
  options.clan.password-store.targetDirectory = lib.mkOption {
    type = lib.types.path;
    default = "/etc/secrets";
    description = ''
      The directory where the password store is uploaded to.
    '';
  };
  config = lib.mkIf (config.clanCore.secretStore == "password-store") {
    clanCore.secretsDirectory = config.clan.password-store.targetDirectory;
    clanCore.secretsUploadDirectory = config.clan.password-store.targetDirectory;
    system.clan.secretsModule = pkgs.writeText "pass.py" ''
      import os
      import subprocess
      from clan_cli.machines.machines import Machine
      from pathlib import Path


      class SecretStore:
          def __init__(self, machine: Machine) -> None:
              self.machine = machine

          def set(self, service: str, name: str, value: str):
              subprocess.run(
                  ["${pkgs.pass}/bin/pass", "insert", "-m", f"machines/{self.machine.name}/{name}"],
                  input=value.encode("utf-8"),
                  check=True,
              )

          def get(self, service: str, name: str) -> str:
              return subprocess.run(
                  ["${pkgs.pass}/bin/pass", "show", f"machines/{self.machine.name}/{name}"],
                  check=True,
                  stdout=subprocess.PIPE,
                  text=True,
              ).stdout

          def exists(self, service: str, name: str) -> bool:
              password_store = os.environ.get("PASSWORD_STORE_DIR", f"{os.environ['HOME']}/.password-store")
              secret_path = Path(password_store) / f"machines/{self.machine.name}/{name}.gpg"
              print(f"checking {secret_path}")
              return secret_path.exists()

          def generate_hash(self) -> str:
              password_store = os.environ.get("PASSWORD_STORE_DIR", f"{os.environ['HOME']}/.password-store")
              hashes = []
              hashes.append(
                  subprocess.run(
                      ["${pkgs.git}/bin/git", "-C", password_store, "log", "-1", "--format=%H", f"machines/{self.machine.name}"],
                      stdout=subprocess.PIPE,
                      text=True,
                  ).stdout.strip()
              )
              for symlink in Path(password_store).glob(f"machines/{self.machine.name}/**/*"):
                  if symlink.is_symlink():
                      hashes.append(
                          subprocess.run(
                              ["${pkgs.git}/bin/git", "-C", password_store, "log", "-1", "--format=%H", symlink],
                              stdout=subprocess.PIPE,
                              text=True,
                          ).stdout.strip()
                      )

              # we sort the hashes to make sure that the order is always the same
              hashes.sort()
              return "\n".join(hashes)

          def update_check(self):
              local_hash = self.generate_hash()
              remote_hash = self.machine.host.run(
                  ["cat", "${config.clan.password-store.targetDirectory}/.pass_info"],
                  check=False,
                  stdout=subprocess.PIPE,
              ).stdout.strip()

              if not remote_hash:
                  print("remote hash is empty")
                  return False

              return local_hash == remote_hash

          def upload(self, output_dir: Path, secrets: list[str, str]) -> None:
              for service, secret in secrets:
                  (output_dir / secret).write_text(self.get(service, secret))
              (output_dir / ".pass_info").write_text(self.generate_hash())
    '';
  };
}

