import json
from pathlib import Path

from ..cmd import run
from ..nix import nix_build, nix_config, nix_eval
from ..ssh import Host, parse_deployment_address


class Machine:
    def __init__(
        self,
        name: str,
        flake: Path | str,
        machine_data: dict | None = None,
    ) -> None:
        """
        Creates a Machine
        @name: the name of the machine
        @clan_dir: the directory of the clan, optional, if not set it will be determined from the current working directory
        @machine_json: can be optionally used to skip evaluation of the machine, location of the json file with machine data
        """
        self.name: str = name
        self.flake: str | Path = flake

        self.eval_cache: dict[str, str] = {}
        self.build_cache: dict[str, Path] = {}

        # TODO do this lazily
        if machine_data is None:
            self.machine_data = json.loads(
                self.build_nix("config.system.clan.deployment.file").read_text()
            )
        else:
            self.machine_data = machine_data

        self.deployment_address = self.machine_data["deploymentAddress"]
        self.secrets_module = self.machine_data.get("secretsModule", None)
        if "secretsData" in self.machine_data:
            self.secrets_data = json.loads(
                Path(self.machine_data["secretsData"]).read_text()
            )
        self.secrets_upload_directory = self.machine_data["secretsUploadDirectory"]

    @property
    def flake_dir(self) -> Path:
        if isinstance(self.flake, Path):
            return self.flake

        if hasattr(self, "flake_path"):
            return Path(self.flake_path)

        print(nix_eval([f"{self.flake}"]))
        self.flake_path = run(nix_eval([f"{self.flake}"])).stdout.strip()
        return Path(self.flake_path)

    @property
    def host(self) -> Host:
        return parse_deployment_address(
            self.name, self.deployment_address, meta={"machine": self}
        )

    def eval_nix(self, attr: str, refresh: bool = False) -> str:
        """
        eval a nix attribute of the machine
        @attr: the attribute to get
        """
        if attr in self.eval_cache and not refresh:
            return self.eval_cache[attr]

        config = nix_config()
        system = config["system"]

        if isinstance(self.flake, Path):
            output = run(
                nix_eval(
                    [
                        f'path:{self.flake}#clanInternals.machines."{system}"."{self.name}".{attr}'
                    ]
                ),
            ).stdout.strip()
        else:
            output = run(
                nix_eval(
                    [
                        f'{self.flake}#clanInternals.machines."{system}"."{self.name}".{attr}'
                    ]
                ),
            ).stdout.strip()
        self.eval_cache[attr] = output
        return output

    def build_nix(self, attr: str, refresh: bool = False) -> Path:
        """
        build a nix attribute of the machine
        @attr: the attribute to get
        """
        if attr in self.build_cache and not refresh:
            return self.build_cache[attr]

        config = nix_config()
        system = config["system"]

        if isinstance(self.flake, Path):
            outpath = run(
                nix_build(
                    [
                        f'path:{self.flake}#clanInternals.machines."{system}"."{self.name}".{attr}'
                    ]
                ),
            ).stdout.strip()
        else:
            outpath = run(
                nix_build(
                    [
                        f'{self.flake}#clanInternals.machines."{system}"."{self.name}".{attr}'
                    ]
                ),
            ).stdout.strip()
        self.build_cache[attr] = Path(outpath)
        return Path(outpath)
