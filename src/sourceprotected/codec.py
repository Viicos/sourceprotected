import codecs
import encodings
import os
from typing import Any, Optional, Tuple

from cryptography.fernet import Fernet

utf_8: codecs.CodecInfo = encodings.search_function("utf8")  # type: ignore[assignment]
if utf_8 is None:
    raise RuntimeError("Unable to find the 'utf8' search function")


def decode(input: bytes, errors: str = "strict") -> Tuple[str, int]:
    if not input:
        return "", 0

    key = os.getenv("SOURCEPROTECTED_KEY")
    if not key:
        raise SyntaxError("Missing 'SOURCEPROTECTED_KEY' environment variable")

    decoded, length = utf_8.decode(input, errors)

    decoded_lines = decoded.split("\n")
    encrypted = ""

    in_block = False

    for line in decoded_lines:
        if "BEGIN SOURCEPROTECTED FILE" in line:
            in_block = True
        elif "END SOURCEPROTECTED FILE" in line:
            break
        elif in_block:
            encrypted += line

    decrypted = Fernet(key).decrypt(encrypted).decode("utf-8")
    if not decrypted.endswith("\n"):
        # It seems the decoded string needs to end with a new line
        # to avoid a `SyntaxError`:
        decrypted += "\n"
    return decrypted, length


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input: Any, errors: str, final: bool) -> Tuple[str, int]:
        if not final:
            return "", 0

        return decode(input, errors)


def search_function(name: str) -> Optional[codecs.CodecInfo]:
    if name == "sourceprotected":
        return codecs.CodecInfo(
            encode=utf_8.encode,
            decode=decode,  # type: ignore[arg-type]
            streamreader=utf_8.streamreader,
            streamwriter=utf_8.streamwriter,
            incrementalencoder=utf_8.incrementalencoder,
            incrementaldecoder=IncrementalDecoder,
            name="sourceprotected",
        )
    return None


def register() -> None:
    codecs.register(search_function)
