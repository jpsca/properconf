from pathlib import Path

from pyceo import Manager, param, option, confirm

from . import secrets as sec
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
from .version import __version__


ENCRYPTED_FILE = "secrets.yaml.enc"
manager = Manager(f"ProperConf v{__version__}", catch_errors=False)


@manager.command(group="setup", name="all")
@option("path", help="Where to create the new project (default is ./config).")
@option("quiet", help="Print nothing to the console.")
def setup(path="./config", quiet=False, _app_env="APP_ENV"):
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

    root_path.mkdir(exist_ok=True, parents=True)

    _setup_init(root_path, _app_env, quiet=quiet)
    setup_env(
        root_path, config=DEFAULT_COMMON_CONFIG, secrets=None, quiet=quiet,
    )
    setup_env(
        root_path / "development",
        config=DEFAULT_DEVELOPMENT_CONFIG,
        secrets=DEFAULT_DEVELOPMENT_SECRETS,
        quiet=quiet,
    )
    secrets = DEFAULT_PRODUCTION_SECRETS.replace("<SECRET_KEY>", sec.generate_token())
    setup_env(
        root_path / "production",
        config=DEFAULT_PRODUCTION_CONFIG,
        secrets=secrets,
        quiet=quiet,
    )
    setup_env(
        root_path / "testing", config=DEFAULT_TESTING_CONFIG, secrets=None, quiet=quiet,
    )
    print("All done! ✨ 🍰 ✨")


@manager.command(group="setup", name="env")
@param("path", help="Folder of the new environment.")
@option("config", help="Optional content of the new config")
@option("secrets", help="Optional (unencrypted) secret content. `None` to disable")
@option("quiet", help="Print nothing to the console.")
def setup_env(path, config="", secrets=DEFAULT_SECRETS, quiet=False):
    """Setup a new env folder with config and secrets.

    Use it if you need more than the defaults environments
    (development, production, and testing.)
    """
    path = Path(path)
    path.mkdir(exist_ok=True, parents=True)
    _setup_config(path, config, quiet=quiet)
    if secrets is not None:
        setup_secrets(path, secrets, quiet=quiet)


def _setup_init(path, app_env, quiet=False):
    fpath = path / "__init__.py"
    if not quiet:
        print(f"Creating {str(fpath)}")
    init = DEFAULT_INIT.replace("APP_ENV", app_env)
    fpath.write_text(init)


def _setup_config(path, config, quiet=False):
    fpath = path / "config.yaml"
    if not quiet:
        print(f"Creating {str(fpath)}")
    fpath.write_text(config)


@manager.command(group="setup", name="secrets")
@param("path", help="Folder of the environment.")
@option("secrets", help="Optional (unencrypted) secret content.")
@option("quiet", help="Print nothing to the console.")
def setup_secrets(path, secrets=DEFAULT_SECRETS, quiet=False):
    """Add a key and encrypted secrets to a folder.
    """
    path = Path(path)
    if not path.exists():
        raise ValueError(f"{path} does not exists")
    fpath = path / ENCRYPTED_FILE
    if not quiet:
        print(f"Creating {str(fpath)}")
    key_file = sec.new_master_key_file(path)
    sec.save_secrets(
        secrets_path=fpath, content=secrets, master_key=key_file,
    )


@manager.command()
@param("path", help="Folder of the environment.")
@option("default", help="Optional (unencrypted) default secrets.")
def edit_secrets(path, default=None):
    """Edit your encrypted secrets.
    """
    filepath = Path(path) / ENCRYPTED_FILE
    if not filepath.exists():
        raise ValueError(f"{filepath} does not exists")
    sec.edit_secrets(filepath, default=default)


@manager.command()
@option("length", help="Length of the secret")
def generate_token(length=sec.SECRET_LENGTH):
    """Generate a secure secret token.

    This value is ideal for a "SECRET_KEY" used
    to sign authentication cookies or similar tasks.
    """
    print(sec.generate_token(length))


@manager.command(name="--version")
def version():
    """Prints the properconf version."""
    print(__version__)


def manager_run():
    manager.run()
