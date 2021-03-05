import copy
from inspect import ismodule
from pathlib import Path

import yaml
try:
    from yaml import CLoader as Loader
except ImportError: # pragma: no cover
    from yaml import Loader

from .main import read_key, read_secrets, ENCRYPTED_FILE


class ConfigDict(dict):
    """A dict that:

    1. Allows `obj.foo` in addition to `obj['foo']` and
       `obj.foo.bar` in addition to `obj['foo']['bar']`.
    3. Improve the `update()` method for deep updating.

    Examples:

    >>> d = ConfigDict({'a': 1, 'b': 2, 'foo': {'b': {'a': 'r'}} })
    >>> d.a
    1
    >>> d.foo
    {'b': {'a': 'r'}}
    >>> d.foo.b.a
    'r'

    """

    def __init__(self, dict_or_iter=None, **kwargs):
        super().__init__()
        self.update(dict_or_iter, **kwargs)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)
        raise AttributeError(
            """Use the obj[key] = value notation to set or update values."""
        )

    def __getattr__(self, key):
        value = self[key]
        if isinstance(value, dict):
            return self.__class__(value)
        return value

    def update(self, src=None, **kwargs):
        if src is None:
            return
        if not hasattr(src, "items"):
            src = dict(src)
        self._deepupdate(self, src)

    def load_object(self, obj):
        """Load values from an object.
        Ignore values that starts with a double underscore or that are
        other python modules.
        """
        values = {
            key: value for key, value in obj.__dict__.items()
            if not key.startswith("__") and not ismodule(value)
        }
        self.update(values)
        return self

    def load_module(self, module):
        """Load values from an module.
        Ignore values that starts with a double underscore or that are
        other python modules.
        """
        return self.load_object(module)

    def load_file(self, filepath):
        """Load values from a YAML file.
        """
        filepath = Path(filepath)
        if not filepath.is_file():
            return self

        content = filepath.read_text()
        data = self._parse_content(content)
        if not isinstance(data, dict):
            raise ValueError("Invalid config at " + str(filepath))
        self.update(data)
        return self

    def load_secrets(self, path, env=""):
        """Load values from an encrypted config file.
        """
        path = Path(path)
        if path.is_file():
            env = path.split(".", 1)[0]
            path = path.parent

        secrets_path = path / (ENCRYPTED_FILE % (env, ))
        if not secrets_path.is_file():
            return self

        key = read_key(path, env)
        content = read_secrets(secrets_path, key)
        data = self._parse_content(content)
        if not isinstance(data, dict):
            raise ValueError("Invalid config at " + str(secrets_path))
        self.update(data)
        return self

    def _deepupdate(self, target, src):
        """Deep update target dict with src.

        For each k,v in src: if k doesn't exist in target, it is deep copied from
        src to target. Otherwise, if v is a dict, recursively deep-update it.

        """
        for key, value in src.items():
            if isinstance(value, dict):
                if key not in target:
                    dict.__setitem__(target, key, copy.deepcopy(value))
                else:
                    self._deepupdate(dict.__getitem__(target, key), value)
            else:
                dict.__setitem__(target, key, copy.copy(value))

    def _parse_content(self, content):
        return yaml.load(content, Loader=Loader) or {}
