import json
import os
import urllib.request
from typing import Any

# Your OpenAI API key
api_key: str = os.environ["OPENAI_API_KEY"]

# The URL to which the request is sent
url: str = "https://api.openai.com/v1/chat/completions"

# The header includes the content type and the authorization with your API key
headers: dict[str, str] = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}


def complete(
    messages: list[dict[str, Any]],
    model: str = "gpt-3.5-turbo",
    temperature: float = 1.0,
) -> str:
    # Data to be sent in the request
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    # Create a request object with the URL and the headers
    req = urllib.request.Request(url, json.dumps(data).encode("utf-8"), headers)

    # Make the request and read the response
    with urllib.request.urlopen(req) as response:
        response_body = response.read()
        resp_data = json.loads(response_body)
        return resp_data["choices"][0]["message"]["content"]


def complete_prompt(
    prompt: str,
    system: str = "",
    model: str = "gpt-3.5-turbo",
    temperature: float = 1.0,
) -> str:
    return complete(
        [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        model,
        temperature,
    )
