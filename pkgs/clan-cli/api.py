import importlib
import json
import pkgutil
from types import ModuleType


def import_all_modules_from_package(pkg: ModuleType) -> None:
    for _loader, module_name, _is_pkg in pkgutil.walk_packages(
        pkg.__path__, prefix=f"{pkg.__name__}."
    ):
        base_name = module_name.split(".")[-1]

        # Skip test modules
        if (
            base_name.startswith("test_")
            or base_name.endswith("_test")
            or base_name == "conftest"
        ):
            continue

        importlib.import_module(module_name)


def main() -> None:
    import clan_cli
    import clan_lib

    import_all_modules_from_package(clan_cli)
    import_all_modules_from_package(clan_lib)

    from clan_lib.api import API

    schema = API.to_json_schema()
    print(f"""{json.dumps(schema, indent=2)}""")


if __name__ == "__main__":
    main()
