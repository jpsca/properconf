from pathlib import Path

from pyceo import Cli, confirm

from . import main
from .defaults import (
    DEFAULT_INIT,
    DEFAULT_SHARED_CONFIG,
    DEFAULT_DEVELOPMENT_CONFIG,
    DEFAULT_PRODUCTION_CONFIG,
    DEFAULT_TESTING_CONFIG,
)
from .version import __version__


__all__ = (
    "manager",
)


class Manager(Cli):
    __doc__ = f"""ProperConf v{__version__}"""

    def setup(self, path="./config", quiet=False, _app_env="APP_ENV"):
        """Set up config files at `PATH` for development, production, and testing environments.

        `setup(path, quiet=False)`

        It will create a `shared.py` and files for development, production
        and testing.

        Arguments:

        - path ["./config"]:
            Where to create the config files.

        - quiet [False]:
            Print nothing to the console.

        """
        root_path = self._setup_root(path, quiet=quiet)
        self._setup_file(root_path / "__init__.py", DEFAULT_INIT.replace("APP_ENV", _app_env))
        self._setup_file(root_path / "shared.py", DEFAULT_SHARED_CONFIG)
        self._setup_file(root_path / "development.py", DEFAULT_DEVELOPMENT_CONFIG)
        self._setup_file(root_path / "production.py", DEFAULT_PRODUCTION_CONFIG)
        self._setup_file(root_path / "testing.py", DEFAULT_TESTING_CONFIG)

    def secrets(self, path, env):
        """Edit your encrypted secrets.

        `secrets(path, env, quiet=False)`

        Arguments:

        - path:
            Root path

        - env:
            Name of the environment (e.g.: "development", "production", etc.)
            It will be used for finding the encrypted file (e.g.: "development.enc.yaml")
            and the key (e.g.: "development.key").

        - quiet [False]:
            Print nothing to the console.

        """
        main.edit_secrets(path, env)

    def token(self, length=main.TOKEN_LENGTH):
        """Generate a secure secret token.

        `token(length=DEFAULT)`

        This value is ideal for a "secret_key" used
        to sign authentication cookies or similar tasks.

        Arguments:

        - length:
            Length of the secret

        """
        print(main.generate_token(length))

    def version(self):
        """Prints the properconf version.
        """
        print(__version__)

    # Private

    def _setup_root(self, path, quiet=False):
        root_path = Path(path)
        if not quiet and root_path.is_dir():
            if not confirm(f"\nWarning: `{path}` folder already exists. Continue?"):
                return
            print()
        if root_path.is_file():
            raise ValueError(f"{path} is an existing file")
        root_path.mkdir(exist_ok=True, parents=True)
        return root_path

    def _setup_file(self, path, text, quiet=False):
        if not quiet:
            print(f"Creating {str(path)}")
        path.write_text(text)


manager = Manager()
