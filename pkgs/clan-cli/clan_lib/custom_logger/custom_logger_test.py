import logging
import threading

from clan_lib.async_run import AsyncContext, set_async_ctx
from clan_lib.custom_logger import PrefixFormatter


def _record(message: str, **extra: str) -> logging.LogRecord:
    record = logging.getLogger("test").makeRecord(
        "test",
        logging.INFO,
        "file.py",
        1,
        message,
        (),
        None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def _format_in_fanout(formatter: PrefixFormatter, record: logging.LogRecord) -> str:
    """Format a record on a thread that carries a fan-out context."""
    formatted: list[str] = []

    def worker() -> None:
        set_async_ctx(AsyncContext(prefix="jon"))
        formatted.append(formatter.format(record))

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()
    return formatted[0]


def test_prefix_comes_from_the_fanout_context() -> None:
    """A line logged inside a per-machine fan-out carries the machine name.

    Only piped subprocess output sets extra["command_prefix"], so without
    the thread-local fallback nearly every line is unattributed.
    """
    formatter = PrefixFormatter()

    assert "[jon]" in _format_in_fanout(formatter, _record("deploying"))
    # the main thread has no fan-out context
    assert "jon" not in formatter.format(_record("deploying"))


def test_extra_command_prefix_wins() -> None:
    formatter = PrefixFormatter()

    formatted = _format_in_fanout(
        formatter,
        _record("subprocess line", command_prefix="sara"),
    )

    assert "[sara]" in formatted
    assert "jon" not in formatted
