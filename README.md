# ProperConf

A modest config system, including support for encrypted secrets.


## Edit secrets

Use `conf secrets PATH ENV`, e.g.: `conf secrets config/ production`.

This will:

1. Search for a `ENV.enc.toml` encrypted file, e.g.: `production.enc.toml`

2. Search for a encription key in this places, in order:
    a) the `MASTER_KEY` environment variable `ENV.key`;
    b) a `ENV.key` file, e.g.: `production.key`;
    c) a `master.key` file.

If an `ENV.enc.toml` encrypted file doesn't exist, it will ask you if it can create an empty one using the encryption key. If it cannot find an encryption key, it also makes a new one in an `ENV.key` file.

Finally, the un-encrypted secrets are loaded in your default text editor so you cna edit them.

### Other commands

#### setup

`conf setup PATH`

Set up config files at `PATH` for development, production, and testing environments.

#### token

`conf token`

Generate a secure secret token.

