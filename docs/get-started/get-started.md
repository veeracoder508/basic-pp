---
icon: lucide/package-open
tags:
  - Get started
  - Setup
--- 

# Get Started


## installation

Basic++ is completely written in python, and is published as a [python package][python package]. 
It is recommended to install it in the python *global environment* when installed [with `pip`][with-pip]
or [with `uv`][with-uv]. Both options automatically install all
necessary dependencies alongside Zensical.

[Python package]: https://pypi.org/project/basic-pp

!!! note "Prerequisites"
    You need to have Python and a Python package manager installed on your
    system before you install Basic++. We recommend you follow the [Python
    Setup and Usage] instructions for your operating system provided on the
    [Python website]. Modern Python distributions include the `pip` package
    manager, so unless you are developing Python software and use `uv`, this is
    the simplest option to install Zensical on your system.

  [with-pip]: #install-with-pip
  [with-uv]: #install-with-uv
  [Python Setup and Usage]: https://docs.python.org/3/using
  [Python website]: https://www.python.org/

### Install with pip { data-toc-label="with pip" }

Zensical can be installed into a virtual environment[^venv] with `pip`.

[^venv]: A [Python virtual environment] is a folder in your project directory that
    contains its own copy of Python and any Python packages the project needs.
    By installing Zensical and its dependencies into a virtual environment you
    ensure that it does not interfere with other projects on your computer that
    also use Python.

  [Python virtual environment]: https://docs.python.org/3/tutorial/venv.html

=== ":material-apple: macOS"
    Open up a terminal window and install Zensical by first setting up a virtual
    environment and then using `pip` to install the Zensical package into it:

    ``` sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install basic-pp
    ```

=== ":fontawesome-brands-windows: Windows"
    Open up a Command Window and install Zensical by first setting up a virtual
    environment and then using `pip` to install the Zensical package into it:

    ``` ps1
    python -m venv .venv  # (1)!
    .venv\Scripts\activate
    pip install basic-pp
    ```

    1.  Depending on your Python installation, you may need to use a different
        binary name such as `python3` or use `py -3`.

=== ":material-linux: Linux"
    Open up a terminal window and install Zensical by first setting up a virtual
    environment and then using `pip` to install the Zensical package into it:

    ``` sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install basic-pp
    ```

### Install with uv { data-toc-label="with uv" }

If you are developing software using Python, chances are you're already using
[`uv`][uv] as a package and project manager, which has become popular in recent
years.

To install Basic++ with `uv` and add it to your development dependencies in
your `pyproject.toml`, use:

  [uv]: https://docs.astral.sh/uv/

```
uv init
uv add --dev zensical
uv run zensical
```

Note that when using Basic++ as a project dependency, you need to always either
use `uv run` or activate the project's virtual environment manually.


!!! tip "Other tools using PyPI"
    There are, of course, other dependency managers and build tools in the
    Python ecosystem that use PyPI as the repository. Installing Basic++ with
    them should be similar to the process of installing with `uv`. Refer to
    their documentation for details.