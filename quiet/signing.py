"""Sign profiles with your own certificate, using the openssl command-line tool."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class SigningError(RuntimeError):
    """Signing could not be completed."""


def sign_profile(src: Path, dst: Path, cert: Path, key: Path, chain: Path | None = None) -> None:
    """Write a DER-signed copy of src to dst. Signing a profile shows the signer's name on install."""
    if shutil.which("openssl") is None:
        raise SigningError("openssl is not installed or not on PATH")
    for path in [cert, key, *([chain] if chain else [])]:
        if not path.is_file():
            raise SigningError(f"file not found: {path}")

    cmd = [
        "openssl", "smime", "-sign",
        "-in", str(src), "-out", str(dst),
        "-signer", str(cert), "-inkey", str(key),
        # -binary stops openssl rewriting line endings (text mode turns LF into CRLF),
        # so the signed profile carries exactly the bytes that were built.
        "-binary", "-nodetach", "-outform", "der",
    ]
    if chain:
        cmd += ["-certfile", str(chain)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        dst.unlink(missing_ok=True)  # never leave a partial file behind
        raise SigningError(f"openssl could not sign the profile: {result.stderr.strip()}")
