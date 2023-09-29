#!/usr/bin/env python
import argparse
import http.client
import json
import sys
from pathlib import Path

ZEROTIER_STATE_DIR = Path("/var/lib/zerotier-one")


class ClanError(Exception):
    pass


# this is managed by the nixos module
def get_network_id() -> str:
    p = Path("/etc/zerotier/network-id")
    if not p.exists():
        raise ClanError(
            f"{p} file not found. Have you enabled the zerotier controller on this host?"
        )
    return p.read_text().strip()


def allow_member(args: argparse.Namespace) -> None:
    member_id = args.member_id
    network_id = get_network_id()
    token = ZEROTIER_STATE_DIR.joinpath("authtoken.secret").read_text()
    conn = http.client.HTTPConnection("localhost", 9993)
    conn.request(
        "POST",
        f"/controller/network/{network_id}/member/{member_id}",
        '{"authorized": true}',
        {"X-ZT1-AUTH": token},
    )
    resp = conn.getresponse()
    if resp.status != 200:
        raise ClanError(
            f"the zerotier daemon returned this error: {resp.status} {resp.reason}"
        )
    print(resp.status, resp.reason)


def list_members(args: argparse.Namespace) -> None:
    network_id = get_network_id()
    networks = ZEROTIER_STATE_DIR / "controller.d" / "network" / network_id / "member"
    if not networks.exists():
        return
    for member in networks.iterdir():
        with member.open() as f:
            data = json.load(f)
            try:
                member_id = data["id"]
            except KeyError:
                raise ClanError(f"error: {member} does not contain an id")
            print(member_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command")
    parser_allow = subparser.add_parser("allow", help="Allow a member to join")
    parser_allow.add_argument("member_id")
    parser_allow.set_defaults(func=allow_member)

    parser_list = subparser.add_parser("list", help="List members")
    parser_list.set_defaults(func=list_members)

    args = parser.parse_args()
    try:
        args.func(args)
    except ClanError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
