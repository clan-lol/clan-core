import ipaddress
from pathlib import Path

NODE_ID_LENGTH = 10
NETWORK_ID_LENGTH = 16


class ZToolError(Exception):
    pass


class Identity:
    """A ZeroTier identity (public + private key pair).

    Construct via from_directory() when loading from a ZeroTier state
    directory, or from_secret_file() when only the secret file is available.
    """

    def __init__(self, public: str, private: str) -> None:
        self.public = public
        self.private = private

    @classmethod
    def from_directory(cls, path: Path) -> "Identity":
        return cls(
            public=(path / "identity.public").read_text(),
            private=(path / "identity.secret").read_text(),
        )

    @classmethod
    def from_secret_file(cls, secret_file: Path) -> "Identity":
        """Load identity from a single identity.secret file.

        The secret file format is node_id:0:public_part:secret_part.
        The public portion is the first three colon-separated fields.
        """
        private = secret_file.read_text()
        public = ":".join(private.split(":")[:3])
        return cls(public=public, private=private)

    def node_id(self) -> str:
        nid = self.public.split(":")[0]
        if len(nid) != NODE_ID_LENGTH:
            msg = f"node_id must be {NODE_ID_LENGTH} characters long, got {len(nid)}: {nid}"
            raise ZToolError(msg)
        return nid


def compute_zerotier_ip(network_id: str, node_id: str) -> ipaddress.IPv6Address:
    if len(network_id) != NETWORK_ID_LENGTH:
        msg = f"network_id must be {NETWORK_ID_LENGTH} characters long, got '{network_id}'"
        raise ZToolError(msg)
    nwid = int(network_id, 16)
    nid = int(node_id, 16)
    addr_parts = bytearray(
        [
            0xFD,
            (nwid >> 56) & 0xFF,
            (nwid >> 48) & 0xFF,
            (nwid >> 40) & 0xFF,
            (nwid >> 32) & 0xFF,
            (nwid >> 24) & 0xFF,
            (nwid >> 16) & 0xFF,
            (nwid >> 8) & 0xFF,
            (nwid) & 0xFF,
            0x99,
            0x93,
            (nid >> 32) & 0xFF,
            (nid >> 24) & 0xFF,
            (nid >> 16) & 0xFF,
            (nid >> 8) & 0xFF,
            (nid) & 0xFF,
        ],
    )
    return ipaddress.IPv6Address(bytes(addr_parts))


def compute_member_id(ipv6_addr: str) -> str:
    addr = ipaddress.IPv6Address(ipv6_addr)
    addr_bytes = bytearray(addr.packed)
    node_id_bytes = addr_bytes[10:16]
    node_id = int.from_bytes(node_id_bytes, byteorder="big")
    return format(node_id, "x").zfill(10)[-10:]
