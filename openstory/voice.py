"""Install verified Turkish voice models on explicit request."""
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


SESLEN_BASE = "https://huggingface.co/seslen-tr/seslen-tts/resolve/2507876ad1c76b30bb7c269fbb4acb8ca365e555/"
SESLEN_HASHES = {
    "metin.onnx": "f89d8a62c4274788105badcdbecf170a2a91a308f4cf3774beff550b85c2548c",
    "ses.onnx": "35e02cb65cf5b3007d84c0d9e21f8f1d424430521a3f8328c2e8037a5c111eea",
    "stiller.npz": "67ec8b23ffa928ae00ad4f60356f5f1657411da7424b07b485b7d92f7c78ea45",
    "sesler.json": "284c9ee754dd22e969b0d47261fd97eda7da02471f6d8bb441205c8638ac77fd",
    "semboller.json": "97dd4e1809503a998803d05ce54fa1fbec94a6d16b41e2f328213778902c2544",
}


def install(folder, piper=False):
    if not piper:
        folder = folder / "seslen"
    base, hashes = (BASE, HASHES) if piper else (SESLEN_BASE, SESLEN_HASHES)
    folder.mkdir(parents=True, exist_ok=True)
    for name, expected in hashes.items():
        dest = folder / name
        if dest.exists() and checksum(dest) == expected:
            continue
        with tempfile.NamedTemporaryFile(dir=folder, delete=False) as tmp:
            partial = Path(tmp.name)
        try:
            with urllib.request.urlopen(base + name, timeout=120) as src, partial.open("wb") as out:
                shutil.copyfileobj(src, out)
            if checksum(partial) != expected:
                raise ValueError(f"İndirilen model özeti uyuşmuyor: {name}")
            os.replace(partial, dest)
        finally:
            partial.unlink(missing_ok=True)
    print(folder / MODEL if piper else folder)
