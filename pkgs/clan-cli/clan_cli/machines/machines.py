import json
import logging
from pathlib import Path

from ..cmd import run
from ..errors import ClanError
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

        self._deployment_info: None | dict[str, str] = deployment_info

    def __str__(self) -> str:
        return f"Machine(name={self.name}, flake={self.flake})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def deployment_info(self) -> dict[str, str]:
        if self._deployment_info is not None:
            return self._deployment_info
        self._deployment_info = json.loads(
            self.build_nix("config.system.clan.deployment.file").read_text()
        )
        return self._deployment_info

    @property
    def target_host_address(self) -> str:
        # deploymentAddress is deprecated.
        val = self.deployment_info.get("targetHost") or self.deployment_info.get(
            "deploymentAddress"
        )
        if val is None:
            msg = f"the 'clan.networking.targetHost' nixos option is not set for machine '{self.name}'"
            raise ClanError(msg)
        return val

    @target_host_address.setter
    def target_host_address(self, value: str) -> None:
        self.deployment_info["targetHost"] = value

    @property
    def secrets_module(self) -> str:
        return self.deployment_info["secretsModule"]

    @property
    def secrets_data(self) -> dict:
        if self.deployment_info["secretsData"]:
            try:
                return json.loads(Path(self.deployment_info["secretsData"]).read_text())
            except json.JSONDecodeError as e:
                raise ClanError(
                    f"Failed to parse secretsData for machine {self.name} as json"
                ) from e
        return {}

    @property
    def secrets_upload_directory(self) -> str:
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
    def target_host(self) -> Host:
        return parse_deployment_address(
            self.name, self.target_host_address, meta={"machine": self}
        )

    @property
    def build_host(self) -> Host:
        """
        The host where the machine is built and deployed from.
        Can be the same as the target host.
        """
        build_host = self.deployment_info.get("buildHost")
        if build_host is None:
            return self.target_host
        # enable ssh agent forwarding to allow the build host to access the target host
        return parse_deployment_address(
            self.name,
            build_host,
            forward_agent=True,
            meta={"machine": self, "target_host": self.target_host},
        )

    def eval_nix(self, attr: str, refresh: bool = False) -> str:
        """
        eval a nix attribute of the machine
        @attr: the attribute to get
        """
        config = nix_config()
        system = config["system"]

        attr = f'clanInternals.machines."{system}".{self.name}.{attr}'

        if attr in self.eval_cache and not refresh:
            return self.eval_cache[attr]

        if isinstance(self.flake, Path):
            if (self.flake / ".git").exists():
                flake = f"git+file://{self.flake}"
            else:
                flake = f"path:{self.flake}"
        else:
            flake = self.flake

        cmd = nix_eval([f"{flake}#{attr}"])

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

        outpath = run(nix_build([f"{flake}#{attr}"])).stdout.strip()
        self.build_cache[attr] = Path(outpath)
        return Path(outpath)
