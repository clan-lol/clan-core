import argparse

from . import register_parser

if __name__ == "__main__":
    # this is use in our integration test
    parser = argparse.ArgumentParser()
    # call the register_parser function, which adds arguments to the parser
    register_parser(parser)
    args = parser.parse_args()

    # call the function that is stored
    # in the func attribute of args, and pass args as the argument
    # look into register_parser to see how this is done
    args.func(args)
