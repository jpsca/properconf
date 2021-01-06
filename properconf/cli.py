from pathlib import Path

from pyceo import Cli, confirm

from . import secrets as sec
from .defaults import (
    DEFAULT_INIT,
    DEFAULT_SHARED_CONFIG,
    DEFAULT_SECRETS,
    DEFAULT_DEVELOPMENT_SECRETS,
    DEFAULT_DEVELOPMENT_CONFIG,
    DEFAULT_PRODUCTION_CONFIG,
    DEFAULT_TESTING_CONFIG,
    DEFAULT_PRODUCTION_SECRETS,
)
from .version import __version__


ENCRYPTED_FILE = "secrets.enc.toml"


class Setup(Cli):

    def all(self, path="./config", split=False, quiet=False, _app_env="APP_ENV"):
        """Setup a proper config project at `path` (./config is the default).

        `all(path, split=False, quiet=False)`

        It will create a `shared.py` and folders for development, production
        and testing, with encripted secrets for development and production.

        Arguments:

        - path ["./config"]:
            Where to create the new project.
        - split [False]:
            Use a different master.key for each environment.
        - quiet [False]:
            Print nothing to the console.

        """
        root_path = Path(path)
        if root_path.is_dir():
            if not confirm(f"\nWarning: `{path}` folder already exists. Continue?"):
                return
            print()
        if root_path.is_file():
            raise ValueError(f"{path} is an existing file")

        root_path.mkdir(exist_ok=True, parents=True)

        self._setup_init(root_path, _app_env, quiet=quiet)

        shared_config = root_path / "shared.py"
        if not quiet:
            print(f"Creating {str(shared_config)}")
        shared_config.write_text(DEFAULT_SHARED_CONFIG)

        if split:
            self._setup_split(root_path, quiet)
        else:
            self._setup_shared(root_path, quiet)

        self.env(
            root_path / "testing", config=DEFAULT_TESTING_CONFIG, secrets=None, quiet=quiet,
        )
        print("All done! ✨ 🍰 ✨")

    def env(self, path, config="", secrets=DEFAULT_SECRETS, master_key=None, quiet=False):
        """Setup a new env folder with config and secrets.

        `env(path, config, secrets=DEFAULT, master_key=None, quiet=False)`

        Use it if you need more than the defaults environments
        (development, production, and testing.)

        Arguments:

        - path:
            Folder of the new environment.
        - config:
            Optional content of the new config.
        - secrets:
            Optional (unencrypted) secret content. `None` to disable.
        - master_key:
            Optional master key.
        - quiet [False]:
            Print nothing to the console.

        """
        path = Path(path)
        path.mkdir(exist_ok=True, parents=True)
        self._setup_config(path, config, quiet=quiet)
        if secrets is not None:
            self.secrets(path, secrets, master_key=master_key, quiet=quiet)

    def secrets(self, path, secrets=DEFAULT_SECRETS, master_key=None, quiet=False):
        """Add a key and encrypted secrets to a folder.

        `secrets(path, secrets=DEFAULT, master_key=None, quiet=False)`

        Arguments:

        - path:
            Folder of the environment.
        - secrets:
            Optional (unencrypted) secret content.
        - master_key:
            Optional master key.
        - quiet [False]:
            Print nothing to the console.

        """
        path = Path(path)
        if not path.exists():
            raise ValueError(f"{path} does not exists")
        fpath = path / ENCRYPTED_FILE
        if not quiet:
            print(f"Creating {str(fpath)}")

        if not master_key:
            if not quiet:
                print(f"Creating {str(path / sec.MASTER_KEY_FILE)}")
            master_key = sec.new_master_key_file(path)

        sec.save_secrets(
            secrets_path=fpath, content=secrets, master_key=master_key,
        )

    # Private

    def _setup_split(self, root_path, quiet, master_key=None):
        self.env(
            root_path / "development",
            config=DEFAULT_DEVELOPMENT_CONFIG,
            secrets=DEFAULT_DEVELOPMENT_SECRETS,
            master_key=master_key,
            quiet=quiet,
        )
        secrets = DEFAULT_PRODUCTION_SECRETS.replace("<SECRET_KEY>", sec.generate_token())
        self.env(
            root_path / "production",
            config=DEFAULT_PRODUCTION_CONFIG,
            secrets=secrets,
            master_key=master_key,
            quiet=quiet,
        )

    def _setup_shared(self, root_path, quiet):
        if not quiet:
            print(f"Creating {str(root_path / sec.MASTER_KEY_FILE)}")
        master_key = sec.new_master_key_file(root_path)
        self.env(
            root_path / "development",
            config=DEFAULT_DEVELOPMENT_CONFIG,
            secrets=None,
            master_key=master_key,
            quiet=quiet,
        )
        secrets = DEFAULT_PRODUCTION_SECRETS.replace("<SECRET_KEY>", sec.generate_token())
        self.env(
            root_path / "production",
            config=DEFAULT_PRODUCTION_CONFIG,
            secrets=secrets,
            master_key=master_key,
            quiet=quiet,
        )

    def _setup_init(self, path, app_env, quiet=False):
        fpath = path / "__init__.py"
        if not quiet:
            print(f"Creating {str(fpath)}")
        init = DEFAULT_INIT.replace("APP_ENV", app_env)
        fpath.write_text(init)


    def _setup_config(self, path, config, quiet=False):
        fpath = path / "__init__.py"
        if not quiet:
            print(f"Creating {str(fpath)}")
        fpath.write_text(config)


class Manager(Cli):
    __doc__ = f"""ProperConf v{__version__}"""

    setup = Setup

    def secrets(self, path, default=None):
        """Edit your encrypted secrets.

        `secrets(path, default=None)`

        Arguments:

        - path:
            Folder of the environment.
        - default:
            Optional (unencrypted) default secrets.

        """
        filepath = Path(path) / ENCRYPTED_FILE
        if not filepath.exists():
            if confirm(f"{filepath} does not exists. Create?", default=False):
                sec.save_secrets(secrets_path=filepath, content=DEFAULT_SECRETS)
            else:
                return
        sec.edit_secrets(filepath, default=default)

    def token(self, length=sec.SECRET_LENGTH):
        """Generate a secure secret token.

        `token(length=DEFAULT)`

        This value is ideal for a "secret_key" used
        to sign authentication cookies or similar tasks.

        Arguments:

        - length:
            Length of the secret

        """
        print(sec.generate_token(length))

    def version(self):
        """Prints the properconf version.
        """
        print(__version__)


manager = Manager()
setup = Setup()
