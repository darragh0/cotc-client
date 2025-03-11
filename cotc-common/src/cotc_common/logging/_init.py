import sys
from json import load
from logging.config import dictConfig
from pathlib import Path

from cotc_common.logging._config import LoggingConfig

LOGGING_PATH: Path = Path(__file__).parent
CONFIG_PATH: Path = LOGGING_PATH / "config.json"


def init_logging(log_cfg: LoggingConfig) -> None:
    """
    Initialize logging for application w/ given configuration.

    Args:
        log_cfg (LoggingConfig): Logging configuration.
    """

    sys.path.append(str(LOGGING_PATH))

    if not CONFIG_PATH.exists():
        msg: str = f"Logging config file not found at {CONFIG_PATH!r}"
        raise FileNotFoundError(msg)

    with Path.open(CONFIG_PATH) as file:
        cfg: dict = load(file)

    if not log_cfg.output_dir.exists():
        log_cfg.output_dir.mkdir(parents=True)

    output_file: str = str(log_cfg.output_dir / f"{log_cfg.file_name}.jsonl")
    cfg["handlers"]["file"]["filename"] = output_file

    for key in cfg["handlers"]:
        if key not in log_cfg.enabled_handlers:
            del cfg["handlers"][key]

    dictConfig(cfg)
