import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Response, status

from clan_cli.webui.schemas import (
    FlakeAction,
    FlakeAttrResponse,
    FlakeResponse,
)

from ...async_cmd import run
from ...flake import create
from ...nix import nix_command, nix_flake_show

router = APIRouter()


async def get_attrs(url: str) -> list[str]:
    cmd = nix_flake_show(url)
    stdout, stderr = await run(cmd)

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
    stdout, stderr = await run(cmd)
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


@router.post("/api/flake/create")
async def create_flake(
    destination: Annotated[Path, Body()], url: Annotated[str, Body()]
) -> Response:
    stdout, stderr = await create.create_flake(destination, url)
    print(stderr.decode("utf-8"), end="")
    print(stdout.decode("utf-8"), end="")
    resp = Response()
    resp.status_code = status.HTTP_201_CREATED
    return resp
