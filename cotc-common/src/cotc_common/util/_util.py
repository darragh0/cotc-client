from datetime import datetime as dt
from datetime import timezone as tz
from enum import IntEnum
from os import name, system
from sys import stderr, stdout
from typing import Any

from cotc_common.util._style import prettify


class ExitCode(IntEnum):
    SUCCESS = 0
    FAILURE = 1
    INVALID_ARGS = 2
    INTERRUPTED = 3
    CONNECTION_REFUSED = 4


def clear_scr() -> None:
    """
    Clear the terminal screen.
    """

    system("cls" if name == "nt" else "clear")


def utc_now() -> dt:
    """
    Get the current UTC time.
    """

    return dt.now(tz.utc)


def pprint(txt: str, *, err: bool = False, **kwargs: Any) -> None:
    """
    Prettify and print given text to either stdout or stderr.

    Args:
        txt (str): Text to print

    Optional Keyword Arguments:
        err (bool): Whether to print to stderr.
        kwargs (Any): Additional arguments to pass to print.
    """
    txt = prettify(txt)
    print(txt, file=stderr if err else stdout, **kwargs)


def print_err(txt: str, **kwargs: Any) -> None:
    """
    Prettify and print given text to stderr.

    Args:
        txt (str): Text to print
        kwargs (Any): Additional arguments to pass to print.
    """
    pprint(txt, err=True, **kwargs)
