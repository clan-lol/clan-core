import json
import logging
from os import path
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep

from clan_cli.dirs import vm_state_dir
from qemu.qmp import QEMUMonitorProtocol

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
        state_dir = vm_state_dir(flake_url=str(self.flake), vm_name=self.name)

        self.qmp_socket: Path = state_dir / "qmp.sock"
        self.qga_socket: Path = state_dir / "qga.sock"

        print(f"qmp_socket: {self.qmp_socket}")
        self._qmp = QEMUMonitorProtocol(path.realpath(self.qmp_socket))
        self._qmp_connected = False

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

    def qmp_connect(self) -> None:
        if not self._qmp_connected:
            tries = 100
            for num in range(tries):
                try:
                    # the socket file link might be outdated, therefore re-init the qmp object
                    self._qmp = QEMUMonitorProtocol(path.realpath(self.qmp_socket))
                    self._qmp.connect()
                    self._qmp_connected = True
                    log.debug("QMP Connected")
                    return
                except FileNotFoundError:
                    if num < 99:
                        sleep(0.1)
                        continue
                    else:
                        raise

    def qmp_command(self, command: str) -> dict:
        self.qmp_connect()
        return self._qmp.command(command)

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

    def nix(
        self,
        method: str,
        attr: str,
        extra_config: None | dict = None,
        impure: bool = False,
    ) -> str | Path:
        """
        Build the machine and return the path to the result
        accepts a secret store and a facts store # TODO
        """
        config = nix_config()
        system = config["system"]

        with NamedTemporaryFile(mode="w") as config_json:
            if extra_config is not None:
                json.dump(extra_config, config_json, indent=2)
            else:
                json.dump({}, config_json)
            config_json.flush()

            nar_hash = json.loads(
                run(
                    nix_eval(
                        [
                            "--impure",
                            "--expr",
                            f'(builtins.fetchTree {{ type = "file"; url = "file://{config_json.name}"; }}).narHash',
                        ]
                    )
                ).stdout.strip()
            )

            args = []

            # get git commit from flake
            if extra_config is not None:
                metadata = nix_metadata(self.flake_dir)
                url = metadata["url"]
                if "dirtyRev" in metadata:
                    if not impure:
                        raise ClanError(
                            "The machine has a dirty revision, and impure mode is not allowed"
                        )
                    else:
                        args += ["--impure"]

                if "dirtyRev" in nix_metadata(self.flake_dir):
                    dirty_rev = nix_metadata(self.flake_dir)["dirtyRevision"]
                    url = f"{url}?rev={dirty_rev}"
                args += [
                    "--expr",
                    f"""
                        ((builtins.getFlake "{url}").clanInternals.machinesFunc."{system}"."{self.name}" {{
                          extraConfig = builtins.fromJSON (builtins.readFile (builtins.fetchTree {{
                            type = "file";
                            url = "{config_json.name}";
                            narHash = "{nar_hash}";
                          }}));
                        }}).{attr}
                    """,
                ]
            else:
                if isinstance(self.flake, Path):
                    if (self.flake / ".git").exists():
                        flake = f"git+file://{self.flake}"
                    else:
                        flake = f"path:{self.flake}"
                else:
                    flake = self.flake
                args += [
                    f'{flake}#clanInternals.machines."{system}".{self.name}.{attr}'
                ]

            if method == "eval":
                output = run(nix_eval(args)).stdout.strip()
                return output
            elif method == "build":
                outpath = run(nix_build(args)).stdout.strip()
                return Path(outpath)
            else:
                raise ValueError(f"Unknown method {method}")

    def eval_nix(
        self,
        attr: str,
        refresh: bool = False,
        extra_config: None | dict = None,
        impure: bool = False,
    ) -> str:
        """
        eval a nix attribute of the machine
        @attr: the attribute to get
        """
        if attr in self.eval_cache and not refresh and extra_config is None:
            return self.eval_cache[attr]

        output = self.nix("eval", attr, extra_config, impure)
        if isinstance(output, str):
            self.eval_cache[attr] = output
            return output
        else:
            raise ClanError("eval_nix returned not a string")

    def build_nix(
        self,
        attr: str,
        refresh: bool = False,
        extra_config: None | dict = None,
        impure: bool = False,
    ) -> Path:
        """
        build a nix attribute of the machine
        @attr: the attribute to get
        """

        if attr in self.build_cache and not refresh and extra_config is None:
            return self.build_cache[attr]

        output = self.nix("build", attr, extra_config, impure)
        if isinstance(output, Path):
            self.build_cache[attr] = output
            return output
        else:
            raise ClanError("build_nix returned not a Path")
