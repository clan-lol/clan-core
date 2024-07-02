import asyncio
import datetime
import json
import logging
import subprocess
from pathlib import Path

import aiohttp
from nio import (
    AsyncClient,
    JoinResponse,
)

from matrix_bot.gitea import (
    GiteaData,
)

from .locked_open import read_locked_file, write_locked_file
from .matrix import MatrixData, send_message
from .openai import create_jsonl_data, upload_and_process_file

log = logging.getLogger(__name__)


def last_ndays_to_today(ndays: int) -> (str, str):
    # Get today's date
    today = datetime.datetime.now()

    # Calculate the date one week ago
    last_week = today - datetime.timedelta(days=ndays)

    # Format both dates to "YYYY-MM-DD"
    todate = today.strftime("%Y-%m-%d")
    fromdate = last_week.strftime("%Y-%m-%d")

    return (fromdate, todate)


def write_file_with_date_prefix(
    content: str, directory: Path, *, ndays: int, suffix: str
) -> Path:
    """
    Write content to a file with the current date as filename prefix.

    :param content: The content to write to the file.
    :param directory: The directory where the file will be saved.
    :return: The path to the created file.
    """
    # Ensure the directory exists
    directory.mkdir(parents=True, exist_ok=True)

    # Get the current date
    fromdate, todate = last_ndays_to_today(ndays)

    # Create the filename
    filename = f"{fromdate}__{todate}_{suffix}.txt"
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


async def git_log(repo_path: str, ndays: int) -> str:
    cmd = [
        "git",
        "log",
        f"--since={ndays} days ago",
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
    last_run_path = data_dir / "last_changelog_run.json"
    last_run = read_locked_file(last_run_path)

    if last_run == {}:
        fromdate, todate = last_ndays_to_today(matrix.changelog_frequency)
        last_run = {
            "fromdate": fromdate,
            "todate": todate,
            "ndays": matrix.changelog_frequency,
        }
        log.debug(f"First run. Setting last_run to {last_run}")
        today = datetime.datetime.now()
        today_weekday = today.strftime("%A")
        if today_weekday != matrix.publish_day:
            log.debug(f"Changelog not due yet. Due on {matrix.publish_day}")
            return
    else:
        last_date = datetime.datetime.strptime(last_run["todate"], "%Y-%m-%d")
        today = datetime.datetime.now()
        today_weekday = today.strftime("%A")
        delta = datetime.timedelta(days=matrix.changelog_frequency)
        if today - last_date <= delta:
            log.debug(f"Changelog not due yet. Due in {delta.days} days")
            return
        elif today_weekday != matrix.publish_day:
            log.debug(f"Changelog not due yet. Due on {matrix.publish_day}")
            return

    # If you made a new room and haven't joined as that user, you can use
    room: JoinResponse = await client.join(matrix.review_room)

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
    diff = await git_log(repo_path, matrix.changelog_frequency)

    fromdate, todate = last_ndays_to_today(matrix.changelog_frequency)
    log.info(f"Generating changelog from {fromdate} to {todate}")

    system_prompt = f"""
Generate a concise changelog for the past week from {fromdate} to {todate},
focusing only on new features and summarizing bug fixes into a single entry.
Ensure the following:

- Deduplicate entries
- Discard uninteresting changes
- Keep the summary as brief as possible
- Use present tense
The changelog is as follows:
---
    """

    # Step 1: Create the JSONL file
    jsonl_data = await create_jsonl_data(user_prompt=diff, system_prompt=system_prompt)

    # Step 2: Upload the JSONL file and process it
    results = await upload_and_process_file(session=http, jsonl_data=jsonl_data)

    # Write the results to a file in the changelogs directory
    result_file = write_file_with_date_prefix(
        json.dumps(results, indent=4),
        data_dir / "changelogs",
        ndays=matrix.changelog_frequency,
        suffix="result",
    )
    log.info(f"LLM result written to: {result_file}")

    # Join responses together
    all_changelogs = []
    for result in results:
        choices = result["response"]["body"]["choices"]
        changelog = "\n".join(choice["message"]["content"] for choice in choices)
        all_changelogs.append(changelog)
    full_changelog = "\n\n".join(all_changelogs)

    # Write the last run to the file
    write_locked_file(last_run_path, last_run)
    log.info(f"Changelog generated:\n{full_changelog}")

    await send_message(client, room, full_changelog)
