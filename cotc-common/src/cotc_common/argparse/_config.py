from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ArgParseArg(BaseModel):
    """
    Single argument for argument parser.
    """

    short_opt: str
    long_opt: str
    metavar: str | None = None
    help: str
    type: type
    default: Any | None = None
    min: Any | None = None
    max: Any | None = None


class ArgParseConfig(BaseModel):
    """
    Configuration for argument parser.
    """

    program_name: str
    version: str
    description: str
    args: list[ArgParseArg]
