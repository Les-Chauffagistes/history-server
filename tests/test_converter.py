import pytest


def test_from_string_to_number_without_unit():
    from historyserver.functions.converter import from_string_to_number

    assert from_string_to_number("1") == 1

def test_from_string_to_number_with_k():
    from historyserver.functions.converter import from_string_to_number

    assert from_string_to_number("12K") == 12_000

def test_from_string_to_number_with_m():
    from historyserver.functions.converter import from_string_to_number

    assert from_string_to_number("6.3M") == 6_300_000

def test_from_string_to_number_with_g():
    from historyserver.functions.converter import from_string_to_number

    assert from_string_to_number("6.3g") == 6_300_000_000

def test_from_string_to_number_with_t():
    from historyserver.functions.converter import from_string_to_number

    assert from_string_to_number("3T") == 3_000_000_000_000

def test_from_string_to_number_with_unknown_unit():
    from historyserver.functions.converter import from_string_to_number

    with pytest.raises(ValueError):
        from_string_to_number("3X")

def test_from_number_to_string():
    from historyserver.functions.converter import from_number_to_string

    assert from_number_to_string(1) == "1"
    assert from_number_to_string(1_000) == "1 K"
    assert from_number_to_string(1_000_000) == "1 M"
    assert from_number_to_string(1_000_000_000) == "1 G"
    assert from_number_to_string(1_000_000_000_000) == "1 T"
    assert from_number_to_string(1_000_000_000_000_000) == "1 P"
    assert from_number_to_string(1_000_000_000_000_000_000) == "1 E"

def test_from_number_to_string_with_decimal():
    from historyserver.functions.converter import from_number_to_string

    assert from_number_to_string(15) == "15"
    assert from_number_to_string(1_500) == "1.5 K"
    assert from_number_to_string(1_010_000) == "1.01 M"