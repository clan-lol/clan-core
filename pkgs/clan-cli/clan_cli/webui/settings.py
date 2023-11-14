import logging
import os
from enum import Enum

log = logging.getLogger(__name__)


class EnvType(Enum):
    production = "production"
    development = "development"

    @staticmethod
    def from_environment() -> "EnvType":
        t = os.environ.get("CLAN_WEBUI_ENV", "production")
        try:
            return EnvType[t]
        except KeyError:
            log.warning(f"Invalid environment type: {t}, fallback to production")
            return EnvType.production

    def is_production(self) -> bool:
        return self == EnvType.production

    def is_development(self) -> bool:
        return self == EnvType.development


class Settings:
    env = EnvType.from_environment()


settings = Settings()
