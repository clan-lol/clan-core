from clan_cli.api import API


def main() -> None:
    schema = API.to_json_schema()
    print(
        f"""export const schema = {schema} as const;
"""
    )


if __name__ == "__main__":
    main()
