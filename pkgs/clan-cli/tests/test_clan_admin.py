import argparse

from clan_cli import admin


def test_make_parser():
    parser = argparse.ArgumentParser()
    admin.register_parser(parser)


# using fp fixture from pytest-subprocess
def test_create(fp):
    cmd = ["nix", "flake", "init", "-t", fp.any()]
    fp.register(cmd)
    args = argparse.Namespace(folder="./my-clan")
    admin.create(args)
    assert fp.call_count(cmd) == 1
