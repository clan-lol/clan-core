# config.py
import logging
import os
from enum import Enum

from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class EnvType(Enum):
    production = "production"
    development = "development"

    @staticmethod
    def from_environment() -> "EnvType":
        t = os.environ.get("CLAN_WEBUI_ENV", "production")
        try:
            return EnvType[t]
        except KeyError:
            logger.warning(f"Invalid environment type: {t}, fallback to production")
            return EnvType.production

    def is_production(self) -> bool:
        return self == EnvType.production

    def is_development(self) -> bool:
        return self == EnvType.development


class Settings(BaseSettings):
    env: EnvType = EnvType.from_environment()
    dev_port: int = int(os.environ.get("CLAN_WEBUI_DEV_PORT", 3000))
    dev_host: str = os.environ.get("CLAN_WEBUI_DEV_HOST", "localhost")


# global instance
settings = Settings()
