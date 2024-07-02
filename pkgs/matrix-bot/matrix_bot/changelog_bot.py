import asyncio
import datetime
import logging
import subprocess
from pathlib import Path
import json
import aiohttp
from nio import (
    AsyncClient,
    JoinResponse,
)

from matrix_bot.gitea import (
    GiteaData,
)

from .matrix import MatrixData, send_message
from .openai import create_jsonl_file, upload_and_process_file

log = logging.getLogger(__name__)


def write_file_with_date_prefix(content: str, directory: Path, suffix: str) -> Path:
    """
    Write content to a file with the current date as filename prefix.

    :param content: The content to write to the file.
    :param directory: The directory where the file will be saved.
    :return: The path to the created file.
    """
    # Ensure the directory exists
    directory.mkdir(parents=True, exist_ok=True)

    # Get the current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create the filename
    filename = f"{current_date}_{suffix}.txt"
    file_path = directory / filename

    # Write the content to the file
    with open(file_path, "w") as file:
        file.write(content)

    return file_path


async def git_pull(repo_path: Path) -> None:
    cmd = ["git", "pull"]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(repo_path),
    )
    await process.wait()


async def git_log(repo_path: str) -> str:
    cmd = [
        "git",
        "log",
        "--since=1 week ago",
        "--pretty=format:%h - %an, %ar : %s",
        "--stat",
        "--patch",
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(
            f"Command '{' '.join(cmd)}' failed with exit code {process.returncode}"
        )

    return stdout.decode()


async def changelog_bot(
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

    repo_path = data_dir / gitea.repo

    if not repo_path.exists():
        cmd = [
            "git",
            "clone",
            f"{gitea.url}/{gitea.owner}/{gitea.repo}.git",
            gitea.repo,
        ]
        subprocess.run(cmd, cwd=data_dir, check=True)

    # git pull
    await git_pull(repo_path)

    # git log
    diff = await git_log(repo_path)

    system_prompt = """
Generate a concise changelog for the past week,
focusing only on new features and summarizing bug fixes into a single entry.
Ensure the following:

- Deduplicate entries
- Discard uninteresting changes
- Keep the summary as brief as possible
- Use present tense
The changelog is as follows:
---
    """

    jsonl_path = data_dir / "changelog.jsonl"

    # Step 1: Create the JSONL file
    await create_jsonl_file(
        user_prompt=diff, system_prompt=system_prompt, jsonl_path=jsonl_path
    )

    # Step 2: Upload the JSONL file and process it
    results = await upload_and_process_file(session=http, jsonl_path=jsonl_path)
    result_file = write_file_with_date_prefix(json.dumps(results, indent=4), data_dir, "result")

    log.info(f"LLM result written to: {result_file}")

    # Join all changelogs with a separator (e.g., two newlines)
    all_changelogs = []
    for result in results:
        choices = result["response"]["body"]["choices"]
        changelog = "\n".join(choice["message"]["content"] for choice in choices)
        all_changelogs.append(changelog)
    full_changelog = "\n\n".join(all_changelogs)


    await send_message(client, room, full_changelog)
