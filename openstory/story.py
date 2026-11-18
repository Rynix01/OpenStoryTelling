"""Read and compose an editable illustrated episode."""
import io
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import resvg_py
from PIL import Image, ImageOps


SHAPES = {"g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
ATTRIBUTES = set("""transform d fill stroke stroke-width stroke-linejoin stroke-linecap
    fill-rule opacity fill-opacity stroke-opacity points x y width height x1 x2 y1 y2
    cx cy rx ry r stroke-dasharray""".split())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded(value, low, high):
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def validate_svg(fragment):
    require(isinstance(fragment, str) and len(fragment) <= 160000, "SVG parçası geçersiz")
    root = ET.fromstring("<g>" + fragment + "</g>")
    for node in root.iter():
        require(node.tag in SHAPES, f"Desteklenmeyen çizim öğesi: {node.tag}")
        for attr, value in node.attrib.items():
            require(attr in ATTRIBUTES and "url(" not in value.lower(), f"Geçersiz SVG niteliği: {attr}")


def validate(data, folder):
    require(isinstance(data, dict) and data.get("version") == 1, "version alanı 1 olmalı")
    for field in ("title", "continuity"):
        require(isinstance(data.get(field), str) and data[field].strip(), f"Eksik alan: {field}")
    require(isinstance(data.get("cast"), dict) and all(isinstance(v, str) for v in data["cast"].values()), "cast nesne olmalı")
    art, boards, shots = (data.get(k) for k in ("art", "boards", "shots"))
    require(isinstance(art, dict) and isinstance(boards, dict), "art ve boards nesne olmalı")
    for name, fragment in art.items():
        require(re.fullmatch(r"[a-zA-Z0-9_-]+", name), "Geçersiz çizim kimliği")
        validate_svg(fragment)
    for name, board in boards.items():
        require(isinstance(board, dict), f"Plan nesne olmalı: {name}")
        if "file" in board:
            path = (folder / board["file"]).resolve()
            require(path.is_relative_to(folder.resolve()) and path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}, f"Görsel bulunamadı: {name}")
        else:
            require(re.fullmatch(r"#[a-fA-F0-9]{6}", board.get("color", "")), f"Zemin rengi gerekli: {name}")
        for layer in board.get("layers", []):
            require(isinstance(layer, dict) and layer.get("art") in art, f"Bilinmeyen çizim: {name}")
            require(layer.get("when", "always") in {"always", "speaking", "blink"}, f"Geçersiz hareket: {name}")
            for field, default, low, high in (("x", 0, -4000, 4000), ("y", 0, -4000, 4000), ("scale", 1, 0.01, 12), ("angle", 0, -360, 360)):
                require(bounded(layer.get(field, default), low, high), f"Geçersiz konum: {name}/{field}")
    require(isinstance(shots, list) and 1 <= len(shots) <= 200, "1–200 plan gerekli")
    for i, shot in enumerate(shots, 1):
        require(isinstance(shot, dict) and shot.get("board") in boards, f"Plan {i}: çizim bulunamadı")
        require(shot.get("camera", "push") in ("push", "pull", "hold"), f"Plan {i}: kamera")
        lines = shot.get("lines")
        require(isinstance(lines, list) and 1 <= len(lines) <= 20 and all(isinstance(s, str) and 0 < len(s.strip()) <= 220 and len(s.split()) <= 24 for s in lines), f"Plan {i}: her satır 1–24 kelime olmalı")
    return data


def read_story(path):
    return validate(json.loads(path.read_text(encoding="utf-8-sig")), path.parent)


def compose(data, name, folder, size=(720, 1280), state="always"):
    board = data["boards"][name]
    if state != "always":
        base = Image.new("RGBA", size)
    elif "file" in board:
        with Image.open(folder / board["file"]) as src:
            base = ImageOps.fit(ImageOps.exif_transpose(src).convert("RGB"), size)
    else:
        base = Image.new("RGB", size, board["color"])
    groups = []
    for layer in board.get("layers", []):
        if layer.get("when", "always") != state:
            continue
        transform = f"translate({layer.get('x', 0)} {layer.get('y', 0)}) rotate({layer.get('angle', 0)}) scale({layer.get('scale', 1)})"
        groups.append(f'<g transform="{transform}">{data["art"][layer["art"]]}</g>')
    if groups:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size[0]}" height="{size[1]}" viewBox="0 0 720 1280">{"".join(groups)}</svg>'
        ink = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg))).convert("RGBA")
        if state == "always":
            base.paste(ink, mask=ink.getchannel("A"))
        else:
            base.alpha_composite(ink)
    return base
