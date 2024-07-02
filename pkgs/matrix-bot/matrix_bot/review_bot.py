import logging

log = logging.getLogger(__name__)
import time
from pathlib import Path

import aiohttp
from nio import (
    AsyncClient,
    JoinResponse,
    MatrixRoom,
    RoomMessageText,
)

from matrix_bot.gitea import (
    GiteaData,
    PullState,
    fetch_pull_requests,
)

from .locked_open import read_locked_file, write_locked_file
from .matrix import MatrixData, get_room_members, send_message


async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    log.debug(
        f"Message received in room {room.display_name}\n"
        f"{room.user_name(event.sender)} | {event.body}"
    )


async def review_requested_bot(
    client: AsyncClient,
    http: aiohttp.ClientSession,
    matrix: MatrixData,
    gitea: GiteaData,
    data_dir: Path,
) -> None:
    # If you made a new room and haven't joined as that user, you can use
    room: JoinResponse = await client.join(matrix.room)

    if not room.transport_response.ok:
        log.error("This can happen if the room doesn't exist or the bot isn't invited")
        raise Exception(f"Failed to join room {room}")

    # Get the members of the room
    users = await get_room_members(client, room)

    # Fetch the pull requests
    tstart = time.time()
    pulls = await fetch_pull_requests(gitea, http, limit=50, state=PullState.ALL)

    # Read the last updated pull request
    last_updated_path = data_dir / "last_updated.json"
    last_updated = read_locked_file(last_updated_path)

    # Check if the pull request is mergeable and needs review
    # and if the pull request is newer than the last updated pull request
    for pull in pulls:
        requested_reviewers = pull["requested_reviewers"]
        if requested_reviewers and pull["mergeable"]:
            if last_updated == {}:
                last_updated = pull
            elif pull["updated_at"] < last_updated["updated_at"]:
                last_updated = pull
            else:
                continue

            # Check if the requested reviewers are in the room
            requested_reviewers = [r["login"].lower() for r in requested_reviewers]
            ping_users = []
            for user in users:
                if user.display_name.lower() in requested_reviewers:
                    ping_users.append(user.user_id)

            # Send a message to the room and mention the users
            log.info(f"Pull request {pull['title']} needs review")
            message = (
                f"Review Requested:\n<code>{pull['title']}</code>\n{pull['html_url']}"
            )
            await send_message(client, room, message, user_ids=ping_users)

            # Write the new last updated pull request
            write_locked_file(last_updated_path, last_updated)

    # Time taken
    tend = time.time()
    tdiff = round(tend - tstart)
    log.debug(f"Time taken: {tdiff}s")
