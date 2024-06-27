import logging

log = logging.getLogger(__name__)
import time
from pathlib import Path
import json
import aiohttp
from nio import (
    AsyncClient,
    JoinResponse,
    JoinedMembersResponse,
    MatrixRoom,
    RoomMessageText,
)

from matrix_bot.gitea import (
    GiteaData,
    PullState,
    fetch_pull_requests,
    fetch_repo_labels,
)

from .locked_open import read_locked_file, write_locked_file
from .matrix import MatrixData, send_message


async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    print(
        f"Message received in room {room.display_name}\n"
        f"{room.user_name(event.sender)} | {event.body}"
    )


async def bot_run(
    client: AsyncClient,
    http: aiohttp.ClientSession,
    matrix: MatrixData,
    gitea: GiteaData,
) -> None:
    # If you made a new room and haven't joined as that user, you can use
    room: JoinResponse = await client.join(matrix.room)

    users: JoinedMembersResponse = await client.joined_members(room.room_id)

    if not users.transport_response.ok:
        raise Exception(f"Failed to get users {users}")

    for user in users.members:
        print(f"User: {user.user_id} {user.display_name}")

    labels = await fetch_repo_labels(gitea, http)
    label_ids: list[int] = []
    for label in labels:
        if label["name"] in gitea.trigger_labels:
            label_ids.append(label["id"])

    tstart = time.time()
    pulls = await fetch_pull_requests(gitea, http, limit=50, state=PullState.ALL)

    last_updated_path = Path("last_updated.json")
    last_updated = read_locked_file(last_updated_path)

    for pull in pulls:
        if pull["requested_reviewers"] and pull["mergeable"]:
            if last_updated == {}:
                last_updated = pull
            elif pull["updated_at"] < last_updated["updated_at"]:
                last_updated = pull
            else:
                continue
            log.info(f"Pull request {pull['title']} needs review")
            message = f"Pull request {pull['title']} needs review\n{pull['html_url']}"
            await send_message(client, room, message, user_ids=["@qubasa:gchq.icu"])

    write_locked_file(last_updated_path, last_updated)

    tend = time.time()
    tdiff = round(tend - tstart)
    log.debug(f"Time taken: {tdiff}s")

    # await client.sync_forever(timeout=30000)  # milliseconds
