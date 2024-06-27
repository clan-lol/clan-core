import logging
from pathlib import Path

import aiohttp

from matrix_bot.gitea import GiteaData
from matrix_bot.matrix import MatrixData

log = logging.getLogger(__name__)

curr_dir = Path(__file__).parent

from nio import (
    AsyncClient,
    ProfileGetAvatarResponse,
    RoomMessageText,
)

from matrix_bot.bot import bot_run, message_callback
from matrix_bot.matrix import set_avatar, upload_image


async def bot_main(
    matrix: MatrixData,
    gitea: GiteaData,
) -> None:
    log.info(f"Connecting to {matrix.server} as {matrix.user}")
    client = AsyncClient(matrix.server, matrix.user)
    client.add_event_callback(message_callback, RoomMessageText)

    log.info(await client.login(matrix.password))

    avatar: ProfileGetAvatarResponse = await client.get_avatar()
    if not avatar.avatar_url:
        mxc_url = await upload_image(client, matrix.avatar)
        log.info(f"Uploaded avatar to {mxc_url}")
        await set_avatar(client, mxc_url)
    else:
        log.info(f"Bot already has an avatar {avatar.avatar_url}")

    try:
        async with aiohttp.ClientSession() as session:
            await bot_run(client, session, matrix, gitea)
    except Exception as e:
        log.exception(e)
    finally:
        await client.close()
