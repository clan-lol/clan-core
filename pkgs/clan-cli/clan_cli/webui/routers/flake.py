import json
from json.decoder import JSONDecodeError
from pathlib import Path

from fastapi import APIRouter, HTTPException

from clan_cli.webui.schemas import FlakeAction, FlakeAttrResponse, FlakeResponse

from ...nix import nix_command, nix_flake_show
from .utils import run_cmd

router = APIRouter()


async def get_attrs(url: str) -> list[str]:
    cmd = nix_flake_show(url)
    stdout = await run_cmd(cmd)

    data: dict[str, dict] = {}
    try:
        data = json.loads(stdout)
    except JSONDecodeError:
        raise HTTPException(status_code=422, detail="Could not load flake.")

    nixos_configs = data.get("nixosConfigurations", {})
    flake_attrs = list(nixos_configs.keys())

    if not flake_attrs:
        raise HTTPException(
            status_code=422, detail="No entry or no attribute: nixosConfigurations"
        )
    return flake_attrs


@router.get("/api/flake/attrs")
async def inspect_flake_attrs(url: str) -> FlakeAttrResponse:
    return FlakeAttrResponse(flake_attrs=await get_attrs(url))


@router.get("/api/flake")
async def inspect_flake(
    url: str,
) -> FlakeResponse:
    actions = []
    # Extract the flake from the given URL
    # We do this by running 'nix flake prefetch {url} --json'
    cmd = nix_command(["flake", "prefetch", url, "--json", "--refresh"])
    stdout = await run_cmd(cmd)
    data: dict[str, str] = json.loads(stdout)

    if data.get("storePath") is None:
        raise HTTPException(status_code=500, detail="Could not load flake")

    content: str
    with open(Path(data.get("storePath", "")) / Path("flake.nix")) as f:
        content = f.read()

    # TODO: Figure out some measure when it is insecure to inspect or create a VM
    actions.append(FlakeAction(id="vms/inspect", uri="api/vms/inspect"))
    actions.append(FlakeAction(id="vms/create", uri="api/vms/create"))

    return FlakeResponse(content=content, actions=actions)
