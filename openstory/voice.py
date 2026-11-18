"""Fetch the two pinned default voice files on explicit request."""
import hashlib
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path


MODEL = "tr_TR-dfki-medium.onnx"
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/"
HASHES = {MODEL: "2844717f524ab965d3fe86e60562cbb601d3e456836efcc2196cc3a14112a8fb",
          MODEL + ".json": "13ebd7810f1b61b5027583cf3131a0a233b6ea81c38f2200ebc4ff41c3cca039"}


def checksum(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def install(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for name, expected in HASHES.items():
        dest = folder / name
        if dest.exists() and checksum(dest) == expected:
            continue
        with tempfile.NamedTemporaryFile(dir=folder, delete=False) as tmp:
            partial = Path(tmp.name)
        try:
            with urllib.request.urlopen(BASE + name, timeout=90) as src, partial.open("wb") as out:
                shutil.copyfileobj(src, out)
            if checksum(partial) != expected:
                raise ValueError(f"İndirilen model özeti uyuşmuyor: {name}")
            os.replace(partial, dest)
        finally:
            partial.unlink(missing_ok=True)
    print(folder / MODEL)
