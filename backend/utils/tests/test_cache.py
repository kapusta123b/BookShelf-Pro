from dataclasses import dataclass

from utils.cache import get_cache_key


@dataclass
class TestFilters:
    test: str
    test2: bool


def test_get_cache_key_return_correct_hash():

    filters = TestFilters(test="test", test2=True)

    correct_hash = "test_698f8c544a7121ef1b9b12a3b980b5c1"

    hash = get_cache_key("test", filters)

    assert correct_hash == hash


def test_get_cache_key_not_contain_prefix():

    filters = TestFilters(test="test", test2=True)

    hash = get_cache_key("", filters)

    assert hash == None


def test_get_cache_key_return_none_when_dataclass_is_empty():
    @dataclass
    class EmptyClass:
        pass

    filters = EmptyClass()

    hash = get_cache_key("test", filters)

    assert hash == None


def test_get_cache_key_return_none_when_class_is_not_a_dataclass():
    class EmptyClass:
        pass

    filters = EmptyClass()

    hash = get_cache_key("test", filters)

    assert hash == None
