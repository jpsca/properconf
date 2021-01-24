from properconf.cli import manager


def test_setup(dst):
    path = dst / "config"
    manager.setup(path)

    assert (path / "__init__.py").is_file()
    assert (path / "shared.py").is_file()
    assert (path / "development.py").is_file()
    assert (path / "production.py").is_file()
    assert (path / "testing.py").is_file()
