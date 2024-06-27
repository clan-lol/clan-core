import logging

log = logging.getLogger(__name__)


from dataclasses import dataclass, field
from enum import Enum

import aiohttp


@dataclass
class GiteaData:
    url: str
    owner: str
    repo: str
    access_token: str | None = None
    trigger_labels: list[str] = field(default_factory=list)


def endpoint_url(gitea: GiteaData, endpoint: str) -> str:
    return f"{gitea.url}/api/v1/repos/{gitea.owner}/{gitea.repo}/{endpoint}"


async def fetch_repo_labels(
    gitea: GiteaData,
    session: aiohttp.ClientSession,
) -> list[dict]:
    """
    Fetch labels from a Gitea repository.

    Returns:
        list: List of labels in the repository.
    """
    url = endpoint_url(gitea, "labels")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if gitea.access_token:
        headers["Authorization"] = f"token {gitea.access_token}"

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            labels = await response.json()
            return labels
        else:
            # You may want to handle different statuses differently
            raise Exception(
                f"Failed to fetch labels: {response.status}, {await response.text()}"
            )


class PullState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


async def fetch_pull_requests(
    gitea: GiteaData,
    session: aiohttp.ClientSession,
    *,
    limit: int,
    state: PullState,
    label_ids: list[int] = [],
) -> list[dict]:
    """
    Fetch pull requests from a Gitea repository.

    Returns:
        list: List of pull requests.
    """
    # You can use the same pattern as fetch_repo_labels
    url = endpoint_url(gitea, "pulls")
    params = {
        "state": state.value,
        "sort": "recentupdate",
        "limit": limit,
        "labels": label_ids,
    }
    headers = {"accept": "application/json"}

    async with session.get(url, params=params, headers=headers) as response:
        if response.status == 200:
            labels = await response.json()
            return labels
        else:
            # You may want to handle different statuses differently
            raise Exception(
                f"Failed to fetch labels: {response.status}, {await response.text()}"
            )
