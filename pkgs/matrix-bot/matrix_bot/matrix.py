import logging
from pathlib import Path

log = logging.getLogger(__name__)

from dataclasses import dataclass

from nio import (
    AsyncClient,
    JoinResponse,
    ProfileSetAvatarResponse,
    RoomSendResponse,
    UploadResponse,
)


async def upload_image(client: AsyncClient, image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        response: UploadResponse
        response, _ = await client.upload(image_file, content_type="image/png")
        if not response.transport_response.ok:
            raise Exception(f"Failed to upload image {response}")
        return response.content_uri  # This is the MXC URL


async def set_avatar(client: AsyncClient, mxc_url: str) -> None:
    response: ProfileSetAvatarResponse
    response = await client.set_avatar(mxc_url)
    if not response.transport_response.ok:
        raise Exception(f"Failed to set avatar {response}")


from nio import AsyncClient


async def send_message(
    client: AsyncClient,
    room: JoinResponse,
    message: str,
    user_ids: list[str] | None = None,
) -> None:
    """
    Send a message in a Matrix room, optionally mentioning users.
    """
    # If user_ids are provided, format the message to mention them
    if user_ids:
        mention_list = ", ".join(
            [
                f"<a href='https://matrix.to/#/{user_id}'>{user_id}</a>"
                for user_id in user_ids
            ]
        )
        body = f"{mention_list}: {message}"
        formatted_body = f"{mention_list}: {message}"
    else:
        body = message
        formatted_body = message

    content = {
        "msgtype": "m.text",
        "format": "org.matrix.custom.html",
        "body": body,
        "formatted_body": formatted_body,
    }

    res: RoomSendResponse = await client.room_send(
        room_id=room.room_id, message_type="m.room.message", content=content
    )

    if not res.transport_response.ok:
        raise Exception(f"Failed to send message {res}")


@dataclass
class MatrixData:
    server: str
    user: str
    avatar: Path
    password: str
    room: str
