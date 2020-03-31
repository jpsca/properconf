data = {
    "title": "Proper Config",
    "name": "proper_config",
    "pypi_name": "proper_config",
    "version": "1.200331",
    "author": "Juan-Pablo Scaletti",
    "author_email": "juanpablo@jpscaletti.com",
    "description": "Config system for web apps.",
    "copyright": "2020",
    "repo_name": "jpscaletti/proper-config",
    "home_url": "https://github.com/jpscaletti/proper-config",
    # Displayed in the pypi project page
    # "project_urls": {
    #     "Documentation": "https://github.com/jpscaletti/proper-form",
    # },

    "development_status": "5 - Production/Stable",
    "minimal_python": 3.6,
    "install_requires": [
        "cryptography ~= 2.5",
        "pyyaml ~= 5.1",
        "texteditor ~= 1.0",
    ],
    "testing_requires": [
        "pytest",
        "pytest-cov",
    ],
    "development_requires": [
        "pytest-flake8",
        "flake8",
        "tox",
    ],
    "entry_points": "",

    "coverage_omit": [],
}

exclude = [
    "hecto.yml",
    "README.md",
    ".git",
    ".git/*",
    ".venv",
    ".venv/*",
    ".DS_Store",
    "CHANGELOG.md",
]


def do_the_thing():
    import hecto

    hecto.copy(
        # "gh:jpscaletti/mastermold.git",
        "../mastermold",  # Path to the local copy of Master Mold
        ".",
        data=data,
        exclude=exclude,
        force=False,
    )


if __name__ == "__main__":
    do_the_thing()
