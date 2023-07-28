import os
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def mock_env(**environ: str) -> Iterator[None]:
    original_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original_environ)
