from clan_lib.machines.suggestions import (
    _levenshtein_distance,
    _suggest_similar_names,
)


def test_identical_strings() -> None:
    assert _levenshtein_distance("hello", "hello") == 0


def test_empty_string() -> None:
    assert _levenshtein_distance("", "") == 0
    assert _levenshtein_distance("hello", "") == 5
    assert _levenshtein_distance("", "world") == 5


def test_single_character_difference() -> None:
    assert _levenshtein_distance("hello", "hallo") == 1  # substitution
    assert _levenshtein_distance("hello", "helloo") == 1  # insertion
    assert _levenshtein_distance("hello", "hell") == 1  # deletion


def test_multiple_differences() -> None:
    assert _levenshtein_distance("kitten", "sitting") == 3
    assert _levenshtein_distance("saturday", "sunday") == 3


def test_case_sensitivity() -> None:
    assert _levenshtein_distance("Hello", "hello") == 1
    assert _levenshtein_distance("HELLO", "hello") == 5


def test_exact_match() -> None:
    candidates = ["machine1", "machine2", "machine3"]
    suggestions = _suggest_similar_names("machine1", candidates)
    assert suggestions[0] == "machine1"


def test_close_match() -> None:
    candidates = ["machine1", "machine2", "machine3"]
    suggestions = _suggest_similar_names("machne1", candidates)  # missing 'i'
    assert "machine1" in suggestions[:2]


def test_case_insensitive_matching() -> None:
    candidates = ["Machine1", "MACHINE2", "machine3"]
    suggestions = _suggest_similar_names("machine1", candidates)
    assert "Machine1" in suggestions[:2]


def test_max_suggestions_limit() -> None:
    candidates = ["aa", "ab", "ac", "ad", "ae"]
    suggestions = _suggest_similar_names("a", candidates, max_suggestions=3)
    assert len(suggestions) <= 3


def test_empty_candidates() -> None:
    suggestions = _suggest_similar_names("test", [])
    assert suggestions == []


def test_realistic_machine_names() -> None:
    candidates = ["web-server", "database", "worker-01", "worker-02", "api-gateway"]

    # Test typo in web-server
    suggestions = _suggest_similar_names("web-sever", candidates)
    assert suggestions[0] == "web-server"

    # Test partial match
    suggestions = _suggest_similar_names("work", candidates)
    worker_suggestions = [s for s in suggestions if "worker" in s]
    assert len(worker_suggestions) >= 2


def test_sorting_by_distance_then_alphabetically() -> None:
    candidates = ["zebra", "apple", "apricot"]
    suggestions = _suggest_similar_names("app", candidates)
    # Both "apple" and "apricot" have same distance (2),
    # but "apple" should come first alphabetically
    apple_index = suggestions.index("apple")
    apricot_index = suggestions.index("apricot")
    assert apple_index < apricot_index
