import os
import time
from argparse import ArgumentParser, Namespace
from pathlib import Path
from textwrap import fill
from typing import Optional

from cryptography.fernet import Fernet

ENCODING_HEADER = "-*- coding: sourceprotected -*-"
BEGIN_HEADER = "-----BEGIN SOURCEPROTECTED FILE-----"
END_HEADER = "-----END SOURCEPROTECTED FILE-----"


class ScriptNamespace(Namespace):
    path: Path
    key: Optional[str]
    inplace: bool
    encryption_time: Optional[int]


def encrypt_source_file(
    inpath: Path, fernet: Fernet, encryption_time: int, outpath: Optional[Path] = None
):
    with open(inpath, "r+b") as infile:
        encrypted = fernet.encrypt_at_time(infile.read(), encryption_time).decode("utf-8")
        # `break_on_hyphens` set to `False` as it can appear in the base64 alphabet
        encrypted_split = fill(
            encrypted, width=len(ENCODING_HEADER), break_on_hyphens=False
        )
        encrypted_source = (
            f"{ENCODING_HEADER}\n\n{BEGIN_HEADER}\n{encrypted_split}\n{END_HEADER}"
        )
        if outpath is None:
            infile.seek(0)
            infile.write(encrypted_source.encode("utf-8"))
        else:
            with open(outpath, "w") as outfile:
                outfile.write(encrypted_source)


def cli():
    parser = ArgumentParser(description="Encrypt Python files using Fernet encryption")
    parser.add_argument(
        "path",
        type=Path,
        help="Source file or directory containing source files to encrypt.",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="URL safe base32/64 encoded key (default: generate a random key).",
    )
    parser.add_argument(
        "--encryption-time",
        type=int,
        help="Provide a custom encryption time, as returned by int(time.time()).",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Encrypt the source files in place. If not set, will write the result "
        "in a newly created file/directory suffixed by '_encrypted'.",
    )

    args = parser.parse_args(namespace=ScriptNamespace())
    key_bytes = (
        args.key.encode("utf-8") if args.key is not None else Fernet.generate_key()
    )
    fernet = Fernet(key_bytes)
    encryption_time = args.encryption_time or int(time.time())

    print(f"Using key: {key_bytes.decode('utf-8')}")
    print(f"Using encryption time: {encryption_time}")

    if args.path.is_file():
        outfile = None
        if not args.inplace:
            outfile = args.path.with_stem(f"{args.path.stem}_encrypted")
        encrypt_source_file(args.path, fernet, encryption_time, outfile)
    else:
        if not args.inplace:
            new_base_root = args.path.with_stem(f"{args.path.stem}_encrypted")
            new_base_root.mkdir()

        for root, dirs, files in os.walk(args.path):
            new_root = None
            if not args.inplace:
                parts = Path(root).parts
                if len(parts) == 1:
                    new_root = new_base_root
                else:
                    new_root = new_base_root.joinpath(*parts[1:])
                    new_root.mkdir(exist_ok=True)

            for file in [file for file in files if file.endswith(".py")]:
                new_path = None
                if new_root is not None:
                    new_path = Path(new_root, file)
                encrypt_source_file(Path(root, file), fernet, encryption_time, new_path)

            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
