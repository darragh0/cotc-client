from __future__ import annotations

import datetime as dt
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final

from pydantic import BaseModel
from cotc_common.util import prettify

if TYPE_CHECKING:
    from types import TracebackType


class LoggingConfig(BaseModel):
    """
    Configuration for application logging.
    """

    output_dir: Path
    file_name: str
    enabled_handlers: list[str]


class StdFormatter(logging.Formatter):
    """
    Formatter for stdout & stderr.
    """

    # COLORS: Final[dict[int, str]] = {
    #     logging.DEBUG: "\033[92m",
    #     logging.INFO: "\033[94m",
    #     logging.WARNING: "\033[93m",
    #     logging.ERROR: "\033[91m",
    #     logging.CRITICAL: "\033[91m",
    # }

    COLORS: Final[dict[int, str]] = {
        logging.DEBUG: "flg",
        logging.INFO: "flb",
        logging.WARNING: "fly",
        logging.ERROR: "flr",
        logging.CRITICAL: "fdr",
    }

    fmt: str | None
    datefmt: str | None

    def __init__(self, *, fmt: str | None = None, datefmt: str | None = None) -> None:
        super().__init__()
        self.fmt: str | None = fmt
        self.datefmt: str | None = "%H:%M:%S" if datefmt is None else datefmt

    def format(self, record: logging.LogRecord) -> str:
        if self.fmt is not None:
            fmt: str = (
                self.fmt.replace("<color>", f"<{StdFormatter.COLORS[record.levelno]}>")
                .replace("</color>", f"</{StdFormatter.COLORS[record.levelno]}>")
            )

        exc_info: (
            tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | None
        )

        if record.exc_info is not None:
            exc_info = record.exc_info
            record.exc_info = None
        else:
            exc_info = None

        formatted: str = logging.Formatter(fmt, datefmt=self.datefmt).format(record)
        record.exc_info = exc_info

        return prettify(formatted)


class JsonFormatter(logging.Formatter):
    """
    Formatter for file output (JSON).
    """

    keys: dict[str, str]

    def __init__(self, *, keys: dict[str, str] | None = None) -> None:
        super().__init__()
        self.keys: dict[str, str] = keys if keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, str] = {}
        keys: dict[str, str] = self.keys.copy()

        if keys.pop("message", None) is not None:
            entry["message"] = record.getMessage()

        if keys.pop("timestamp", None) is not None:
            entry["timestamp"] = dt.datetime.fromtimestamp(
                record.created,
                tz=dt.timezone.utc,
            ).isoformat()

        entry.update(
            {key: getattr(record, val) for key, val in keys.items()},
        )

        if record.exc_info is not None:
            entry["exception"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            entry["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(entry, default=str)


class DismissErrorsFilter(logging.Filter):
    """
    Filter for dismissing errors.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.WARNING
