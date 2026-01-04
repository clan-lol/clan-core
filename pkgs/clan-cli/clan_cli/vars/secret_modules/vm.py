# Re-export shim for backwards compatibility
# DONT add any more modules here
from clan_lib.vars.secret_modules.vm import SecretStore

__all__ = ["SecretStore"]
