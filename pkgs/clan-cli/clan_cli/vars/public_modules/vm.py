# Re-export shim for backwards compatibility
# DONT add any more modules here
from clan_lib.vars.public_modules.vm import VarsStore

__all__ = ["VarsStore"]
