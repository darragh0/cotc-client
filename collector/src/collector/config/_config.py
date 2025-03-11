from pathlib import Path
from typing import Final

from cotc_common.config import BaseConfig, init_base_config
from pydantic import BaseModel

ROOT_PATH: Final[Path] = Path(__file__).parent.parent


class AppConfig(BaseModel):
    weather_endpoint: str
    city: str
    api_key: str


class Config(BaseConfig):
    app: AppConfig


def init_config() -> Config:
    base_cfg, app_cfg = init_base_config(ROOT_PATH)

    return Config(
        app=AppConfig(**app_cfg),
        argparse=base_cfg.argparse,
        argv=base_cfg.argv,
        logging=base_cfg.logging,
    )
