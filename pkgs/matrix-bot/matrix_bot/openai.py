import asyncio
import json
import logging
import os
from pathlib import Path

import aiohttp

log = logging.getLogger(__name__)

# The URL to which the request is sent
url: str = "https://api.openai.com/v1/chat/completions"


def api_key() -> str:
    if "OPENAI_API_KEY" not in os.environ:
        raise Exception("OPENAI_API_KEY not set. Please set it in your environment.")
    return os.environ["OPENAI_API_KEY"]


from typing import Any

import aiofiles


async def create_jsonl_file(
    *,
    user_prompt: str,
    system_prompt: str,
    jsonl_path: Path,
    model: str = "gpt-4o",
    max_tokens: int = 1000,
) -> None:
    """
    Read the content of a file and create a JSONL file with a request to summarize the content.

    :param jsonl_path: The path where the JSONL file will be saved.
    :param model: The model to use for summarization.
    :param max_tokens: The maximum number of tokens for the summary.
    """

    summary_request = {
        "custom_id": "request-1",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
        },
    }

    async with aiofiles.open(jsonl_path, "w") as f:
        await f.write(json.dumps(summary_request) + "\n")


async def upload_and_process_file(
    *, session: aiohttp.ClientSession, jsonl_path: Path, api_key: str = api_key()
) -> dict[str, Any]:
    """
    Upload a JSONL file to OpenAI's Batch API and process it asynchronously.

    :param session: An aiohttp.ClientSession object.
    :param jsonl_path: The path of the JSONL file to upload.
    :param api_key: OpenAI API key for authentication.
    :return: The response from the Batch API.
    """
    # Step 1: Upload the JSONL file to OpenAI's Files API
    async with aiofiles.open(jsonl_path, "rb") as f:
        file_data = await f.read()

    upload_url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    data = aiohttp.FormData()
    data.add_field(
        "file", file_data, filename=jsonl_path.name, content_type="application/jsonl"
    )
    data.add_field("purpose", "batch")

    async with session.post(upload_url, headers=headers, data=data) as response:
        if response.status != 200:
            raise Exception(f"File upload failed with status code {response.status}")
        upload_response = await response.json()
        file_id = upload_response.get("id")

    if not file_id:
        raise Exception("File ID not returned from upload")

    # Step 2: Create a batch using the uploaded file ID
    batch_url = "https://api.openai.com/v1/batches"
    batch_data = {
        "input_file_id": file_id,
        "endpoint": "/v1/chat/completions",
        "completion_window": "24h",
    }

    async with session.post(batch_url, headers=headers, json=batch_data) as response:
        if response.status != 200:
            raise Exception(f"Batch creation failed with status code {response.status}")
        batch_response = await response.json()
        batch_id = batch_response.get("id")

    if not batch_id:
        raise Exception("Batch ID not returned from creation")

    # Step 3: Check the status of the batch until completion
    status_url = f"https://api.openai.com/v1/batches/{batch_id}"

    while True:
        async with session.get(status_url, headers=headers) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to check batch status with status code {response.status}"
                )
            status_response = await response.json()
            status = status_response.get("status")
            if status in ["completed", "failed", "expired"]:
                break
            await asyncio.sleep(10)  # Wait before checking again

    if status != "completed":
        raise Exception(f"Batch processing failed with status: {status}")

    # Step 4: Retrieve the results
    output_file_id = status_response.get("output_file_id")
    output_url = f"https://api.openai.com/v1/files/{output_file_id}/content"

    async with session.get(output_url, headers=headers) as response:
        if response.status != 200:
            raise Exception(
                f"Failed to retrieve batch results with status code {response.status}"
            )

        # Read content as text
        content = await response.text()

    # Parse the content as JSONL
    results = [json.loads(line) for line in content.splitlines()]
    return results
