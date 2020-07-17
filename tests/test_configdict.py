import pytest

from properconf import ConfigDict


def test_dict_init():
    config = ConfigDict({"a": 1, "B": 2, "foo": {"B": {"a": "r"}}})

    assert config.a == 1
    assert config.foo == {"B": {"a": "r"}}
    assert config.foo.B.a == "r"


def test_iter_init():
    config = ConfigDict([("a", 1), ("B", 2), ("foo", {"B": {"a": "r"}})])

    assert config.a == 1
    assert config.foo == {"B": {"a": "r"}}
    assert config.foo.B.a == "r"


def test_do_not_set_attributes():
    config = ConfigDict()

    with pytest.raises(AttributeError):
        config.foo = "bar"


def test_can_set_underscore_attributes():
    config = ConfigDict()
    config._foo = "bar"

    assert config._foo == "bar"


def test_deep_update():
    config = ConfigDict(
        {
            "auth": {"hash": "sha1", "rounds": 123},
            "users": ["foo", "bar"],
            "a": 1,
            "foo": "bar",
        }
    )
    config.update(
        {
            "auth": {"hash": "argon2"},
            "users": ["lorem", "ipsum"],
            "a": 2,
            "fizz": {"buzz": 3},
        }
    )

    assert config == {
        "auth": {"hash": "argon2", "rounds": 123},
        "users": ["lorem", "ipsum"],
        "a": 2,
        "foo": "bar",
        "fizz": {"buzz": 3},
    }
