import argparse

from . import register_parser

if __name__ == "__main__":
    # this is use in our integration test
    parser = argparse.ArgumentParser()
    register_parser(parser)
    args = parser.parse_args()
    args.func(args)
