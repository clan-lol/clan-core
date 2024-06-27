import json

# some unused imports are needed to trigger registrations of api functions
import clan_cli.config.schema  # noqa: F401
from clan_cli.api import API


def main() -> None:
    schema = API.to_json_schema()
    print(
        f"""export const schema = {json.dumps(schema, indent=2)} as const;
"""
    )


if __name__ == "__main__":
    main()
