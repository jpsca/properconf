import os
import string
from pathlib import Path

from pyceo import Manager, param, option, confirm

from .defaults import (
    DEFAULT_INIT,
    DEFAULT_COMMON_CONFIG,
    DEFAULT_SECRETS,
    DEFAULT_DEVELOPMENT_SECRETS,
    DEFAULT_DEVELOPMENT_CONFIG,
    DEFAULT_PRODUCTION_CONFIG,
    DEFAULT_TESTING_CONFIG,
    DEFAULT_PRODUCTION_SECRETS,
)
from .secrets import new_master_key_file, save_secrets
from .version import __version__


manager = Manager(
    f"ProperConf v{__version__}",
    catch_errors=False
)


@manager.command()
@option("path", help="Where to create the new project (default is ./config).")
def setup(path="./config", _app_env="APP_ENV"):
    """Setup a proper config project at `path` (./config is the default).

    It will create a `common.yaml` and folders for development, production
    and testing, with encripted secrets for development and production.
    """
    root_path = Path(path)
    if root_path.is_dir():
        if not confirm(f"\nWarning: `{path}` folder already exists. Continue?"):
            return
        print()
    if root_path.is_file():
        raise ValueError(f"{path} is an existing file")
    root_path.mkdir(exist_ok=True)

    _setup_init(root_path, _app_env)
    setup_env(
        root_path,
        config=DEFAULT_COMMON_CONFIG,
        secrets=None,
    )

    setup_env(
        root_path / "development",
        config=DEFAULT_DEVELOPMENT_CONFIG,
        secrets=DEFAULT_DEVELOPMENT_SECRETS,
    )

    secrets = DEFAULT_PRODUCTION_SECRETS.replace("<SECRET_KEY>", _generate_token())
    setup_env(
        root_path / "production",
        config=DEFAULT_PRODUCTION_CONFIG,
        secrets=secrets,
    )

    setup_env(
        root_path / "testing",
        config=DEFAULT_TESTING_CONFIG,
        secrets=None,
    )

    print("All done! ✨ 🍰 ✨")


@manager.command()
@param("path", help="Folder of the new environment.")
@option("config", help="Optional content of the new config")
@option("secrets", help="Optional (unencrypted) secret content. `None` to disable")
def setup_env(path, config="", secrets=DEFAULT_SECRETS):
    """Setup a new env folder with config and secrets.

    Use it if you need more than the defaults environments
    (development, production, and testing.)
    """
    path.mkdir(exist_ok=True)
    _setup_config(path, config)
    if secrets is not None:
        setup_secrets(path, secrets)


def _setup_init(path, app_env):
    fpath = path / "__init__.py"
    print(f"Creating {str(fpath)}")
    init = DEFAULT_INIT.replace("APP_ENV", app_env)
    fpath.write_text(init)


def _setup_config(path, config):
    fpath = path / "config.yaml"
    print(f"Creating {str(fpath)}")
    fpath.write_text(config)


@manager.command()
@param("path", help="Folder of the environment.")
@option("secrets", help="Optional (unencrypted) secret content.")
def setup_secrets(path, secrets=DEFAULT_SECRETS):
    """Add a key and encrypted secrets to a folder.
    """
    fpath = path / "secrets.yaml.enc"
    print(f"Creating {str(fpath)}")
    key_file = new_master_key_file(path)
    save_secrets(
        secrets_path=fpath,
        content=secrets,
        master_key=key_file,
    )


CHARS = string.ascii_letters + string.digits + "&*"
CHARS_LEN = 64
SECRET_LENGTH = 64


def _generate_token(length=SECRET_LENGTH):
    return "".join([CHARS[ord(os.urandom(1)) % CHARS_LEN] for i in range(length)])


@manager.command()
@option("length", help="Length of the secret")
def generate_secret_token(length=SECRET_LENGTH):
    """Generate a secure secret"""
    print(_generate_token(length))


@manager.command(name="--version")
def version():
    """Prints the properconf version."""
    print(__version__)


def manager_run():
    manager.run()
