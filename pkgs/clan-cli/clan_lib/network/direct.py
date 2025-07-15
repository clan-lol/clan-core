from clan_lib.network.network import NetworkTechnologyBase


class NetworkTechnology(NetworkTechnologyBase):
    """Direct network connection technology - checks SSH connectivity"""

    def is_running(self) -> bool:
        """Direct connections are always 'running' as they don't require a daemon"""
        return True
