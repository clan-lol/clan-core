import argparse

import clan_admin


def test_make_parser():
    parser = argparse.ArgumentParser()
    clan_admin.make_parser(parser)


# using fp fixture from pytest-subprocess
def test_create(fp):
    cmd = ["nix", "flake", "init", "-t", fp.any()]
    fp.register(cmd)
    args = argparse.Namespace(folder="./my-clan")
    clan_admin.create(args)
    assert fp.call_count(cmd) == 1
