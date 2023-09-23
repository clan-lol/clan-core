import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from clan_cli.webui.schemas import FlakeAction, FlakeResponse

from ...nix import nix_command

router = APIRouter()


@router.get("/api/flake")
async def inspect_flake(
    url: str,
) -> FlakeResponse:
    actions = []
    # Extract the flake from the given URL
    # We do this by running 'nix flake prefetch {url} --json'
    cmd = nix_command(["flake", "prefetch", url, "--json"])
    proc = await asyncio.create_subprocess_exec(
        cmd[0],
        *cmd[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(stderr))

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
