import json
import logging
from pathlib import Path

from ..cmd import run
from ..nix import nix_build, nix_config, nix_eval, nix_metadata
from ..ssh import Host, parse_deployment_address

log = logging.getLogger(__name__)


class Machine:
    def __init__(
        self,
        name: str,
        flake: Path | str,
        deployment_info: dict | None = None,
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

        if deployment_info is not None:
            self.deployment_info = deployment_info

    def __str__(self) -> str:
        return f"Machine(name={self.name}, flake={self.flake})"

    def __repr__(self) -> str:
        return str(self)

    def get_deployment_info(self) -> None:
        self.deployment_info = json.loads(
            self.build_nix("config.system.clan.deployment.file").read_text()
        )
        print(f"self_deployment_info: {self.deployment_info}")

    @property
    def deployment_address(self) -> str:
        if not hasattr(self, "deployment_info"):
            self.get_deployment_info()
        return self.deployment_info["deploymentAddress"]

    @property
    def secrets_module(self) -> str:
        if not hasattr(self, "deployment_info"):
            self.get_deployment_info()
        print(f"self_deployment_info2: {self.deployment_info}")
        return self.deployment_info["secretsModule"]

    @property
    def secrets_data(self) -> dict:
        if not hasattr(self, "deployment_info"):
            self.get_deployment_info()
        if self.deployment_info["secretsData"]:
            try:
                return json.loads(Path(self.deployment_info["secretsData"]).read_text())
            except json.JSONDecodeError:
                log.error(
                    f"Failed to parse secretsData for machine {self.name} as json"
                )
                return {}
        return {}

    @property
    def secrets_upload_directory(self) -> str:
        if not hasattr(self, "deployment_info"):
            self.get_deployment_info()
        return self.deployment_info["secretsUploadDirectory"]

    @property
    def flake_dir(self) -> Path:
        if isinstance(self.flake, Path):
            return self.flake

        if hasattr(self, "flake_path"):
            return Path(self.flake_path)

        self.flake_path = nix_metadata(self.flake)["path"]
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
        config = nix_config()
        system = config["system"]

        attr = f'clanInternals.machines."{system}".{self.name}.{attr}'
        print(f"attr: {attr}")

        if attr in self.eval_cache and not refresh:
            return self.eval_cache[attr]

        if isinstance(self.flake, Path):
            if (self.flake / ".git").exists():
                flake = f"git+file://{self.flake}"
            else:
                flake = f"path:{self.flake}"
        else:
            flake = self.flake

        print(f"evaluating {flake}#{attr}")
        cmd = nix_eval([f"{flake}#{attr}"])
        print(f"cmd: {cmd}")
        output = run(cmd).stdout.strip()
        self.eval_cache[attr] = output
        return output

    def build_nix(self, attr: str, refresh: bool = False) -> Path:
        """
        build a nix attribute of the machine
        @attr: the attribute to get
        """

        config = nix_config()
        system = config["system"]

        attr = f'clanInternals.machines."{system}".{self.name}.{attr}'

        if attr in self.build_cache and not refresh:
            return self.build_cache[attr]

        if isinstance(self.flake, Path):
            flake = f"path:{self.flake}"
        else:
            flake = self.flake

        log.info(f"building {flake}#{attr}")
        outpath = run(nix_build([f"{flake}#{attr}"])).stdout.strip()
        self.build_cache[attr] = Path(outpath)
        return Path(outpath)
