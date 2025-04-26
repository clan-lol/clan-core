import json

from clan_lib.api import API


def main() -> None:
    schema = API.to_json_schema()
    print(f"""{json.dumps(schema, indent=2)}""")


if __name__ == "__main__":
    main()
