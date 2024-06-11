import json
from dataclasses import dataclass
from pathlib import Path

from clan_cli.api import API
from clan_cli.clan.create import ClanMetaInfo
from clan_cli.errors import ClanError


@dataclass
class UpdateOptions:
    directory: str
    meta: ClanMetaInfo | None = None


@API.register
def update_clan_meta(options: UpdateOptions) -> ClanMetaInfo:
    meta_file = Path(options.directory) / Path("clan/meta.json")
    if not meta_file.exists():
        raise ClanError(
            "File not found",
            description=f"Could not find {meta_file} to update.",
            location="update_clan_meta",
        )

    meta_content: dict[str, str] = {}
    with open(meta_file) as f:
        meta_content = json.load(f)

    meta_content = {**meta_content, **options.meta.__dict__}

    with open(meta_file) as f:
        json.dump(meta_content, f)

    return ClanMetaInfo(**meta_content)
