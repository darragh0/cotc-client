from argparse import Namespace
from json import load
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from cotc_common.argparse import ArgParseArg, ArgParseConfig, init_argparse
from cotc_common.logging import LoggingConfig, init_logging
from cotc_common.types import JSONObj


class BaseConfig(BaseModel):
    """
    Base configuration for all applications.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    argparse: ArgParseConfig
    argv: Namespace
    logging: LoggingConfig


def init_base_config(root_path: Path) -> tuple[BaseConfig, JSONObj]:
    """
    Initialize base configuration from config file.

    Args:
        root_path (Path): Root path of project.

    Returns:
        tuple[BaseConfig, JSONObj]: Base configuration object & app configuration.
    """

    config_path: Path = root_path / "config/config.json"

    if not config_path.exists():
        msg: str = f"Config file not found at {config_path!r}"
        raise FileNotFoundError(msg)

    with Path.open(config_path) as file:
        cfg: dict = load(file)

    # Init logging
    cfg["logging"]["output_dir"] = root_path / cfg["logging"]["output_dir"]
    log_cfg: LoggingConfig = LoggingConfig(**cfg["logging"])
    init_logging(log_cfg)

    # Init argparse
    ap_args: list[ArgParseArg] = []
    if "args" in cfg["argparse"]:
        for arg in cfg["argparse"]["args"]:
            arg["type"] = eval(arg["type"])
            ap_args.append(ArgParseArg(**arg))

    ap_cfg: ArgParseConfig = ArgParseConfig(
        program_name=cfg["argparse"]["program_name"],
        version=cfg["argparse"]["version"],
        description=cfg["argparse"]["description"],
        args=ap_args,
    )
    argv: Namespace = init_argparse(ap_cfg)

    return BaseConfig(argparse=ap_cfg, argv=argv, logging=log_cfg), cfg["app"]
