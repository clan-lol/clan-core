import argparse
import http.client
import json
import sys
from pathlib import Path

from zerotier_tools import ZToolError, compute_member_id, compute_zerotier_ip

ZEROTIER_STATE_DIR = Path("/var/lib/zerotier-one")
HTTP_OK = 200


# This is managed by the nixos module
def get_network_id(args: argparse.Namespace) -> str:
    if args.network_id:
        return args.network_id
    p = Path("/etc/zerotier/network-id")
    if not p.exists():
        msg = f"{p} not found. Pass --network-id or ensure the file exists."
        raise ZToolError(msg)
    return p.read_text().strip()


def allow_member(args: argparse.Namespace) -> None:
    if args.member_ip:
        member_id = compute_member_id(args.member_id_or_ip)
    else:
        if not args.member_id_or_ip:
            msg = "Either --member-ip or member_id_or_ip must be provided"
            raise ZToolError(msg)
        member_id = args.member_id_or_ip
    network_id = get_network_id(args)
    token = ZEROTIER_STATE_DIR.joinpath("authtoken.secret").read_text()
    conn = http.client.HTTPConnection("localhost", 9993)
    conn.request(
        "POST",
        f"/controller/network/{network_id}/member/{member_id}",
        '{"authorized": true}',
        {"X-ZT1-AUTH": token},
    )
    resp = conn.getresponse()
    if resp.status != HTTP_OK:
        msg = f"the zerotier daemon returned this error: {resp.status} {resp.reason}"
        raise ZToolError(msg)
    print(resp.status, resp.reason)


def list_members(args: argparse.Namespace) -> None:
    network_id = get_network_id(args)
    networks = ZEROTIER_STATE_DIR / "controller.d" / "network" / network_id / "member"
    if not networks.exists():
        return
    if not args.no_headers:
        print(f"{'Member ID':<10} {'Ipv6 Address':<39} {'Authorized'}")
    for member in networks.iterdir():
        with member.open() as f:
            data = json.load(f)
            try:
                member_id = data["id"]
            except KeyError as e:
                msg = f"error: {member} does not contain an id"
                raise ZToolError(msg) from e
            ip = str(compute_zerotier_ip(network_id, member_id))
            authorized = str(data.get("authorized", False))
            print(f"{member_id:<10} {ip:<39} {authorized}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage zerotier members")
    parser.add_argument(
        "--network-id",
        type=str,
        required=False,
        help="ZeroTier network ID (falls back to /etc/zerotier/network-id)",
    )
    subparser = parser.add_subparsers(dest="command", required=True)
    parser_allow = subparser.add_parser("allow", help="Allow a member to join")
    parser_allow.add_argument(
        "--member-ip",
        help="Interpret the positional argument as an IPv6 address instead of member ID",
        action="store_true",
    )
    parser_allow.add_argument(
        "member_id_or_ip",
        help="Member ID or IPv6 address (when --member-ip is used)",
    )
    parser_allow.set_defaults(func=allow_member)

    parser_list = subparser.add_parser("list", help="List members")
    parser_list.add_argument(
        "--no-headers",
        action="store_true",
        help="Do not print headers",
    )
    parser_list.set_defaults(func=list_members)

    args = parser.parse_args()
    try:
        args.func(args)
    except ZToolError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
