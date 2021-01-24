
import os

import pytest

from properconf import main, defaults


def test_new_master_key_file(dst):
    key_path = dst / "my.key"
    key = main.new_key_file(key_path)

    assert key_path.is_file()
    assert key_path.read_bytes() == key


def test_read_master_key_from_file(dst):
    key_path = dst / "dev.key"
    key = main.new_key_file(key_path)

    assert main.read_key(dst, "dev") == key


def test_read_master_key_from_env(dst):
    key = main.generate_key()
    os.environ[main.MASTER_KEY_ENV] = key.decode("utf8")

    assert main.read_key(dst) == key
    del os.environ[main.MASTER_KEY_ENV]


def test_key_env_over_file(dst):
    key_env = main.generate_key()
    os.environ[main.MASTER_KEY_ENV] = key_env.decode("utf8")
    key_path = dst / "dev.key"
    key_file = main.new_key_file(key_path)

    assert key_file != key_env
    assert main.read_key(dst, "dev") == key_env
    del os.environ[main.MASTER_KEY_ENV]


def test_read_secrets(dst):
    key = main.generate_key()
    secrets_path = dst / "main.enc"
    my_secrets = "This will be encrypted"
    main.save_secrets(secrets_path, key, my_secrets)

    assert main.read_secrets(secrets_path, key) == my_secrets


def test_read_empty_secrets(dst):
    key = main.generate_key()
    secrets_path = dst / "main.enc"
    main.save_secrets(secrets_path, key, "")

    assert main.read_secrets(secrets_path, key) == ""


def test_read_invalid_secrets(dst):
    key = main.generate_key()
    secrets_path = dst / "main.enc"
    secrets_path.write_bytes(b"this is invalid")

    with pytest.raises(Exception):
        main.read_secrets(secrets_path, key)
