import cProfile
import io
import logging
import os
import pstats
import re
from collections.abc import Callable
from typing import Any

# Ensure you have a logger set up for logging exceptions
log = logging.getLogger(__name__)


def trim_path_to_three_levels(path: str) -> str:
    parts = path.split(os.path.sep)
    if len(parts) > 4:
        return os.path.sep.join(parts[-4:])
    else:
        return path


def profile(func: Callable) -> Callable:
    """
    A decorator that profiles the decorated function, printing out the profiling
    results with paths trimmed to three directories deep.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        pr = cProfile.Profile()
        res: Any = None
        try:
            pr.enable()
            res = func(*args, **kwargs)
            pr.disable()
        except Exception as ex:
            log.exception(ex)
            pr.disable()
            return None

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(12)

        # Process the output to trim file paths
        output_lines = s.getvalue().split("\n")
        for line in output_lines:
            try:
                parts = re.split(r"\s+", line)[
                    1:
                ]  # Split on the first space to separate the time from the path
                fqpath = parts[-1]
                fpath, line_num = fqpath.split(":")
                if os.path.sep in fpath:  # Check if this looks like it includes a path
                    fpath = trim_path_to_three_levels(fpath)
                    prefix = f"{parts[0]:>7}"
                    prefix += f"{parts[1]:>9}"
                    prefix += f"{parts[2]:>9}"
                    prefix += f"{parts[3]:>9}"
                    prefix += f"{parts[4]:>9}"
                    new_line = f"{prefix:}   {fpath}:{line_num}"
                else:
                    new_line = line
            except (ValueError, IndexError):
                new_line = line  # If there's no path, leave the line as is
            print(new_line)
        return res

    return wrapper
