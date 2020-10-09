from properconf.cli import setup_all


def test_setup_all(dst):
    config = dst / "config"
    setup_all(config)

    assert (config / "__init__.py").is_file()
    assert (config / "shared.toml").is_file()
    assert (config / "master.key").is_file()

    assert (config / "development" / "config.toml").is_file()
    assert (config / "development" / "secrets.enc.toml").is_file()

    assert (config / "production" / "config.toml").is_file()
    assert (config / "production" / "secrets.enc.toml").is_file()

    assert (config / "testing" / "config.toml").is_file()


def test_setup_all_split(dst):
    config = dst / "config"
    setup_all(config, split=True)

    assert (config / "__init__.py").is_file()
    assert (config / "shared.toml").is_file()
    assert not (config / "master.key").exists()

    assert (config / "development" / "config.toml").is_file()
    assert (config / "development" / "secrets.enc.toml").is_file()
    master_key_1 = config / "development" / "master.key"
    assert master_key_1.is_file()

    assert (config / "production" / "config.toml").is_file()
    assert (config / "production" / "secrets.enc.toml").is_file()
    master_key_2 = config / "production" / "master.key"
    assert master_key_2.is_file()

    assert (config / "testing" / "config.toml").is_file()

    assert master_key_1.read_bytes() != master_key_2.read_bytes()
