#!/usr/bin/env python3

import json

from clan_lib.api import load_in_all_api_functions


def main() -> None:
    load_in_all_api_functions()

    # import lazily since we otherwise we do not have all api functions loaded according to Qubasa
    from clan_lib.api import API  # noqa: PLC0415

    schema = API.to_json_schema()
    print(f"""{json.dumps(schema, indent=2)}""")


if __name__ == "__main__":
    main()
