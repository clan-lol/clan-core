import pytest
from api import TestClient


@pytest.mark.impure
def test_static_files(api: TestClient) -> None:
    response = api.get("/")
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    response = api.get("/does-no-exists.txt")
    assert response.status_code == 404
