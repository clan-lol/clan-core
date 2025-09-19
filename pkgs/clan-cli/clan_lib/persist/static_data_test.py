from clan_lib.persist.static_data import calculate_static_data


def test_calculate_static_data_basic() -> None:
    all_values = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "optionB": False,
            "listSetting": [1, 2, 3, 4],
        },
        "staticOnly": "staticValue",
    }
    persisted = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [2, 3],
        },
    }

    expected_static = {
        "settings.optionB": False,
        "settings.listSetting": [1, 4],
        "staticOnly": "staticValue",
    }

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_static_data_no_static() -> None:
    all_values = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [1, 2, 3],
        },
    }
    persisted = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [1, 2, 3],
        },
    }

    expected_static: dict = {}

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_static_data_all_static() -> None:
    all_values = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [1, 2, 3],
        },
        "staticOnly": "staticValue",
    }
    persisted: dict = {}

    expected_static = {
        "name": "example",
        "version": 1,
        "settings.optionA": True,
        "settings.listSetting": [1, 2, 3],
        "staticOnly": "staticValue",
    }

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_static_data_empty_all_values() -> None:
    # This should never happen in practice, but we test it for completeness.
    # Maybe this should emit a warning in the future?
    all_values: dict = {}
    persisted = {
        "name": "example",
        "version": 1,
    }

    expected_static: dict = {}

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_nested_dicts() -> None:
    all_values = {
        "level1": {
            "level2": {
                "staticKey": "staticValue",
                "persistedKey": "persistedValue",
            },
            "anotherStatic": 42,
        },
        "topLevelStatic": True,
    }
    persisted = {
        "level1": {
            "level2": {
                "persistedKey": "persistedValue",
            },
        },
    }

    expected_static = {
        "level1.level2.staticKey": "staticValue",
        "level1.anotherStatic": 42,
        "topLevelStatic": True,
    }

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_dot_in_keys() -> None:
    # TODO: This is a bug in the current implementation.
    # We need to change the key representation to handle this case correctly.
    # For now, we just document the behavior with this test.
    all_values = {
        "key.foo": "staticValue",
        "key": {
            "foo": "anotherStaticValue",
        },
    }
    persisted: dict = {}

    expected_static = {
        "key.foo": "anotherStaticValue",
    }

    static_data = calculate_static_data(all_values, persisted)

    assert static_data == expected_static
