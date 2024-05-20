from clan_cli import create_parser
from clan_cli.api import API
from clan_cli.api.schema_compat import to_json_schema


def main() -> None:
    # Create the parser to register the API functions
    create_parser()

    schema = to_json_schema(API._registry)
    print(
        f"""export const schema = {schema} as const;
"""
    )


if __name__ == "__main__":
    main()
