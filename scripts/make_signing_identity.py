"""Makes a free signing identity for your own iPhone, so profiles you sign show "Signed by" there.

Run it on your own computer, which needs openssl:

    python3 scripts/make_signing_identity.py

It writes three files to a folder outside this project (default: ~/quiet-signing):

  key.pem                        your private key. Keep it private. Never share it or put it in git.
  cert.pem                       your signing certificate.
  trust-on-iphone.mobileconfig   a profile that installs cert.pem on your iPhone as a trusted certificate.

Then sign the profiles with it:

    python3 -m quiet presets --sign ~/quiet-signing/cert.pem ~/quiet-signing/key.pem

This is free. It works only on iPhones where you install trust-on-iphone.mobileconfig and turn trust on.
Profiles you sign show "Not Verified" on anyone else's iPhone. A paid certificate from a trusted authority
is the only way to make the signature trusted for everyone.
"""

from __future__ import annotations

import argparse
import os
import plistlib
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FILES = ("key.pem", "cert.pem", "trust-on-iphone.mobileconfig")
# Plain letters, digits, spaces and a little punctuation, so the certificate name stays simple.
NAME_RULE = re.compile(r"^[A-Za-z0-9 ,.'-]{1,64}$")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def openssl(args: list[str]) -> bytes:
    result = subprocess.run(["openssl", *args], capture_output=True)
    if result.returncode != 0:
        fail(f"openssl failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def trust_profile(der: bytes, name: str) -> bytes:
    """A profile that installs the certificate as a trusted root on the iPhone."""
    root = {
        "PayloadType": "com.apple.security.root",
        "PayloadVersion": 1,
        "PayloadIdentifier": "com.quiet.signing.trust.root",
        "PayloadUUID": str(uuid.uuid4()).upper(),
        "PayloadDisplayName": f"{name} certificate",
        "PayloadContent": der,
    }
    profile = {
        "PayloadContent": [root],
        "PayloadDescription": "Trusts the certificate that signs Quiet DNS profiles on this iPhone.",
        "PayloadDisplayName": f"{name} trust",
        "PayloadIdentifier": "com.quiet.signing.trust",
        "PayloadOrganization": "Quiet",
        "PayloadRemovalDisallowed": False,
        "PayloadScope": "System",
        "PayloadType": "Configuration",
        "PayloadUUID": str(uuid.uuid4()).upper(),
        "PayloadVersion": 1,
    }
    return plistlib.dumps(profile, fmt=plistlib.FMT_XML)


def main() -> None:
    parser = argparse.ArgumentParser(description="Make a free signing identity for your own iPhone.")
    parser.add_argument("--folder", type=Path, default=Path.home() / "quiet-signing",
                        help="where to write the files (default: ~/quiet-signing)")
    parser.add_argument("--name", default="Quiet DNS personal signing",
                        help="the name iPhone shows as the signer")
    parser.add_argument("--years", type=int, default=2, help="how long the certificate is valid")
    args = parser.parse_args()

    if not NAME_RULE.match(args.name):
        fail("the name can use letters, digits, spaces and , . ' - only, up to 64 characters")
    if not 1 <= args.years <= 10:
        fail("--years must be between 1 and 10")
    if shutil.which("openssl") is None:
        fail("openssl is not installed or not on PATH")

    folder = args.folder.expanduser().resolve()
    try:
        folder.relative_to(PROJECT)
        fail("choose a folder outside the Quiet project, so the key can't be committed by accident")
    except ValueError:
        pass
    existing = [name for name in FILES if (folder / name).exists()]
    if existing:
        fail(f"{folder} already has {', '.join(existing)}. Choose another folder, or move these files first.")

    folder.mkdir(parents=True, exist_ok=True)
    os.chmod(folder, 0o700)
    key, cert = folder / "key.pem", folder / "cert.pem"

    old_umask = os.umask(0o077)  # the key is never readable by other users, even for a moment
    try:
        openssl(["req", "-x509", "-newkey", "rsa:2048", "-nodes",
                 "-keyout", str(key), "-out", str(cert),
                 "-days", str(365 * args.years), "-subj", f"/CN={args.name}"])
    finally:
        os.umask(old_umask)
    os.chmod(key, 0o600)

    der = openssl(["x509", "-in", str(cert), "-outform", "DER"])
    trust_path = folder / "trust-on-iphone.mobileconfig"
    trust_path.write_bytes(trust_profile(der, args.name))

    print(f"wrote {key} (private: keep it secret)")
    print(f"wrote {cert}")
    print(f"wrote {trust_path}")
    print()
    print("Next, on your iPhone:")
    print("  1. Send yourself trust-on-iphone.mobileconfig (AirDrop works) and open it.")
    print("  2. Settings > Downloaded Profile > Install. Allow the warning that it isn't signed.")
    print("  3. Settings > General > About > Certificate Trust Settings. Turn on the entry for your name, if it's listed.")
    print()
    print("Then sign the profiles from the project folder:")
    print(f"  python3 -m quiet presets --sign {cert} {key}")


if __name__ == "__main__":
    main()
