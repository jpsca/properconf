import os
import string


CHARS = string.ascii_letters + string.digits + "&*"
CHARS_LEN = 64
SECRET_KEY_LEN = 64


def generate_secret_key(key_len=SECRET_KEY_LEN):
    return "".join([CHARS[ord(os.urandom(1)) % CHARS_LEN] for i in range(key_len)])


DEFAULT_SECRETS = """# This is an encrypted YAML file.
#
# Your can safely store here credentials like API keys and such,
# and commit this file to your source version control system.
# -------------------------------------------------------------

# foo: "bar"
"""

DEFAULT_DEVELOPMENT_SECRETS = DEFAULT_SECRETS


def get_default_production_secrets():
    return DEFAULT_SECRETS + f'SECRET_KEY: "{generate_secret_key()}"\n'


DEFAULT_COMMON_CONFIG = """# Shared config
# -------------------------------------------------------------

DEBUG: false
"""

DEFAULT_DEVELOPMENT_CONFIG = """# Development config
# -------------------------------------------------------------

DEBUG: true
SECRET_KEY: "---- This is a fake secret key just for development ----"
"""

DEFAULT_PRODUCTION_CONFIG = """# Production config
# -------------------------------------------------------------

DEBUG: false
SECRET_KEY: NULL  # Set in secrets
"""

DEFAULT_TESTING_CONFIG = """# Testing config
# -------------------------------------------------------------

DEBUG: false
SECRET_KEY: "---- This is a fake secret key just for testing ----"
"""

DEFAULT_INIT = """from pathlib import Path

from properconf import ConfigDict


def load_config(env):
    root_path = Path(__file__).parent
    config = ConfigDict()
    config.load_file(root_path / "common.yaml")
    config.load_file(root_path / env / "config.yaml")
    config.load_secrets(root_path / env / "secrets.yaml.enc")
    return config


env = os.getenv("APP_ENV", "development")
config = load_config(env)
"""
