import os

import pytest

from properconf import secrets


def test_new_master_key_file(dst):
    key = secrets.new_master_key_file(dst)
    key_path = dst / secrets.MASTER_KEY_FILE

    assert key_path.is_file()
    assert key_path.read_bytes() == key


def test_read_master_key_from_file(dst):
    key = secrets.new_master_key_file(dst)
    assert secrets.read_master_key(dst) == key


def test_read_master_key_from_env(dst):
    key = secrets.generate_key()
    os.environ[secrets.MASTER_KEY_ENV] = key.decode("utf8")
    assert secrets.read_master_key(dst) == key
    del os.environ[secrets.MASTER_KEY_ENV]


def test_key_env_over_file(dst):
    key_env = secrets.generate_key()
    os.environ[secrets.MASTER_KEY_ENV] = key_env.decode("utf8")

    key_file = secrets.new_master_key_file(dst)

    assert key_file != key_env
    assert secrets.read_master_key(dst) == key_env
    del os.environ[secrets.MASTER_KEY_ENV]


def test_read_secrets(dst):
    secrets.new_master_key_file(dst)
    secrets_path = dst / "secrets.enc"
    my_secrets = "This will be encrypted"
    secrets.save_secrets(secrets_path, my_secrets)

    assert secrets.read_secrets(secrets_path) == my_secrets


def test_read_empty_secrets(dst):
    secrets.new_master_key_file(dst)
    secrets_path = dst / "secrets.enc"
    secrets.save_secrets(secrets_path, "")

    assert secrets.read_secrets(secrets_path) == ""


def test_read_empty_secrets_no_key(dst):
    secrets_path = dst / "secrets.enc"
    secrets_path.touch()

    assert secrets.read_secrets(secrets_path) == ""


def test_read_no_secrets(dst):
    secrets_path = dst / "secrets.enc"

    with pytest.raises(Exception):
        secrets.read_secrets(secrets_path)


def test_read_secrets_but_no_key(dst):
    secrets_path = dst / "secrets.enc"
    secrets_path.write_text("whatever")

    with pytest.raises(IOError):
        secrets.read_secrets(secrets_path)


def test_read_invalid_secrets(dst):
    secrets_path = dst / "secrets.enc"
    secrets_path.write_bytes(b"this is invalid")
    secrets.new_master_key_file(dst)

    with pytest.raises(Exception):
        secrets.read_secrets(secrets_path)
