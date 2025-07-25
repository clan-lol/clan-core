#!/usr/bin/env python3

import json

from clan_lib.api import load_in_all_api_functions


def main() -> None:
    load_in_all_api_functions()

    from clan_lib.api import API

    schema = API.to_json_schema()
    print(f"""{json.dumps(schema, indent=2)}""")


if __name__ == "__main__":
    main()
