import copy
import os
import queue
import re
import string
from pathlib import Path

from cryptography.fernet import Fernet
from pyceo import confirm
import texteditor
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError: # pragma: no cover
    from yaml import Loader, Dumper

from .defaults import DEFAULT_SECRETS, DEFAULT_ENCRIPTED_HEADER


__all__ = (
    "edit_secrets",
    "read_key",
    "read_secrets",
    "save_secrets",
    "new_key_file",
    "generate_key",
    "generate_token",
    "MASTER_KEY_FILE",
    "MASTER_KEY_ENV",
)

INTRO_MSG = """You can edit your secrets now, do not forget to save your changes."""
ENCRYPTED_FILE = "%s.enc.yaml"
KEY_FILE = "%s.key"
MASTER_KEY_FILE = "master.key"
MASTER_KEY_ENV = "MASTER_KEY"


def edit_secrets(
    path,
    env,
    *,
    quiet=False,
    default=DEFAULT_SECRETS,
    secrets_header=DEFAULT_ENCRIPTED_HEADER,
    master_key_env=MASTER_KEY_ENV,
    intro_msg=INTRO_MSG,
):
    """Edit your encrypted secrets in the default text editor."""
    path = Path(path)
    filepath = path / (ENCRYPTED_FILE % (env,))
    key = read_key(path, env, master_key_env=master_key_env)
    keyfile = KEY_FILE % (env,)

    if filepath.exists():
        if not key:
            raise IOError(
                f"Key not found. Either put a `{keyfile}` or a `{MASTER_KEY_FILE}`"
                " beside your encrypted secrets, or set and environment"
                f" variable `{master_key_env}` with the key value"
                " (the environment variable takes precendence over the file)."
            )
        content = read_secrets(filepath, key) or default
    else:
        if quiet or not confirm(f"{filepath} does not exists. Create?", default=False):
            return
        if not key:
            key = new_key_file(path / keyfile)
        content = default

    if not quiet and intro_msg:
        print(intro_msg)
    new_content = texteditor.open(content, extension=filepath.suffix)
    save_secrets(filepath, key, new_content, header=secrets_header)


def read_key(path, env=None, master_key_env=MASTER_KEY_ENV):
    key = os.getenv(master_key_env, "").strip().encode("utf8")
    path = Path(path)

    if not key and env:
        keyfile = KEY_FILE % (env,)
        keypath = path / keyfile
        if keypath.is_file():
            key = keypath.read_bytes().strip()

    if not key:
        keypath = path / MASTER_KEY_FILE
        if keypath.is_file():
            key = keypath.read_bytes().strip()

    return key


RX_COMMENT = re.compile(rb"\s*#[^\n]*\n")


def read_secrets(filepath, key):
    filepath = Path(filepath)
    enc_content = RX_COMMENT.sub(b"", filepath.read_bytes()).strip()
    if not enc_content:
        return ""
    content = Fernet(key).decrypt(enc_content)
    return content.decode("utf8")


def save_secrets(filepath, key, content, header=DEFAULT_ENCRIPTED_HEADER):
    filepath = Path(filepath)
    enc_content = Fernet(key).encrypt(content.encode("utf8"))
    filepath.write_bytes(header.encode("utf8"))
    skeleton_header = get_skeleton_header(content)
    with filepath.open("ab") as f:
        f.write(skeleton_header.encode("utf8"))
        f.write(b"\n#\n")
        f.write(enc_content)


def get_skeleton_header(content):
    try:
        config = yaml.load(content, Loader=Loader) or {}
    except (TypeError, ValueError):
        print(
            "-- WARNING: The encrypted config has syntax errors and"
            " is not a valid YAML file."
        )
        return ""

    sk = get_skeleton(config)
    text = yaml.dump(sk, Dumper=Dumper).strip()
    return "#  " + "\n#  ".join(text.split("\n"))


Queue = getattr(queue, "SimpleQueue", queue.Queue)


def get_skeleton(config, maxdepth=2, empty="..."):
    """Takes a dict and return another with all the non-dict values
    or those deeper than `maxdepth` replaced by `empty`.
    """
    dicts = Queue()
    skeleton = copy.deepcopy(config)
    dicts.put((0, skeleton))

    while dicts.qsize() > 0:
        level, subdict = dicts.get()
        for key, value in subdict.items():
            if level < maxdepth and isinstance(value, dict):
                dicts.put((level + 1, value))
                continue
            subdict[key] = empty

    return skeleton


def new_key_file(filepath):
    key = generate_key()
    Path(filepath).write_bytes(key)
    return key


def generate_key():
    return Fernet.generate_key()


CHARS = string.ascii_letters + string.digits + "&*"
CHARS_LEN = 64
TOKEN_LENGTH = 64


def generate_token(length=TOKEN_LENGTH):
    return "".join([CHARS[ord(os.urandom(1)) % CHARS_LEN] for i in range(length)])
