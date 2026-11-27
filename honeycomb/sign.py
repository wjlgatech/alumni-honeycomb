"""Signed feeds: each hive signs its public feed with its own Ed25519 key, so any mirror or relay can carry it untrusted.

Why now: with thousands of schools, feeds travel through mirrors (a mainland-China copy, relays run by strangers). A
signature lets anyone check a feed came from that hive and was not changed, without trusting the host and without a
blockchain. Ed25519 signatures are deterministic, so the `.sig` file is drift-gated like the feed itself.

  keygen(path)               write a new private key (PEM) to `path`, return the public key (base64)
  sign(text, key_path)       detached signature (base64) of the exact feed text
  verify(text, sig, pubkey)  True only if the signature matches that public key

Private keys live in hives-private/keys/ (gitignored). The simulated hives commit TEST keys, marked as such.
"""

from __future__ import annotations

import base64
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def public_of(key: Ed25519PrivateKey) -> str:
    """The raw public key, base64: what the registry lists for a hive."""
    raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(raw).decode()


def keygen(path: Path) -> str:
    """Create a private key file (mode 600) and return its public key."""
    key = Ed25519PrivateKey.generate()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                       serialization.NoEncryption()))
    path.chmod(0o600)
    return public_of(key)


def _load(path: Path) -> Ed25519PrivateKey:
    """Read an Ed25519 private key from a PEM file."""
    key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError(f"{path} is not an Ed25519 key")
    return key


def sign(text: str, key_path: Path) -> str:
    """Detached signature over the exact UTF-8 bytes of the feed."""
    return base64.b64encode(_load(key_path).sign(text.encode("utf-8"))).decode() + "\n"


def verify(text: str, sig: str, pubkey: str) -> bool:
    """True when `sig` is a valid signature of `text` by `pubkey`; False on any mismatch or malformed input."""
    try:
        Ed25519PublicKey.from_public_bytes(base64.b64decode(pubkey)).verify(base64.b64decode(sig.strip()), text.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError):
        return False
