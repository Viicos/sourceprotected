# sourceprotected

Encrypt Python source files and decrypt them on the fly during runtime.

[![Python versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Usage

## Installation

Using `pip`:

```sh
pip install sourceprotected
```

### Encrypting the source files

```sh
sourceprotected path/to/src(.py)
Using key: fHC79...
Using encryption time: 1694...
```

### Decrypt during runtime

With `sourceprotected` installed in your current environment, you can run/import encrypted files/modules as long as the `SOURCEPROTECTED_KEY` environment variable is set:

`encrypted.py`:

```python
# -*- coding: sourceprotected -*-

-----BEGIN SOURCEPROTECTED FILE-----
gAAAAABk-eJaJarzMWy70GTRkRi6kjaD-zJy
-fHX_0G5VHTZjEKxJUvFhVWfWpX_j3LydmJo
pn7YrAj5CSqqPWgxUY_dSk5ELA==
-----END SOURCEPROTECTED FILE-----
```

`main.py`:

```python
import encrypted  # Will decrypt encrypted.py on the fly.
```

Finally:

```sh
SOURCEPROTECTED_KEY=Bk92p... python -B main.py
```

## How does it work?

`sourceprotected` uses a custom [codec](https://docs.python.org/3/library/codecs.html) that will decrypt the file content using the `SOURCEPROTECTED_KEY` environment variable.

This codec is registered on startup by using a [`.pth`](https://docs.python.org/3/library/site.html) file.

Credits goes to https://github.com/asottile-archive/future-fstrings for the implementation idea.
