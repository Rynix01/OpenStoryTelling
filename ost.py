"""OpenStoryTelling command line."""
import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from openstory.author import brief, generate
from openstory.render import render
from openstory.story import compose, read_story
from openstory.voice import MODEL, install
from openstory.stage import draw_actors


def main():
    cli = argparse.ArgumentParser(description="OpenStoryTelling · Türkçe çizgi hikâye atölyesi")
    sub = cli.add_subparsers(dest="command", required=True)
    voice = sub.add_parser("voice", help="Türkçe karakter seslerini indir veya doğrula")
    voice.add_argument("--piper", action="store_true", help="Eski tek sesli bölümler için Piper kur")
    voice.add_argument("--dir", type=Path, default=Path("models"))
    for name in ("brief", "generate", "make"):
        author = sub.add_parser(name, help={"brief":"Sohbet için bölüm isteği hazırla", "generate":"Codex CLI ile bölüm yaz ve çiz", "make":"Fikirden proje ve MP4 üret"}[name])
        author.add_argument("idea")
        author.add_argument("--previous", type=Path)
        if name in ("generate", "make"):
            author.add_argument("-o", "--output", type=Path, required=True)
            author.add_argument("--codex-model", default=os.environ.get("OPENSTORY_CODEX_MODEL"), help="Codex CLI oturumunda kullanılabilen model")
        if name == "make":
            author.add_argument("--model", type=Path, default=Path("models/seslen"))
            author.add_argument("--music-seed")
    for name in ("check", "preview", "render"):
        action = sub.add_parser(name, help={"check":"Bölüm dosyasını doğrula", "preview":"Bir planı PNG olarak çiz", "render":"Seslendir ve MP4 üret"}[name])
        action.add_argument("story", type=Path)
        if name != "check":
            action.add_argument("-o", "--output", type=Path, required=True)
        if name == "preview":
            action.add_argument("--shot", type=int, default=1)
        if name == "render":
            action.add_argument("--model", type=Path)
            action.add_argument("--pace", type=float, default=1.0, help="Piper süre çarpanı (0.7–1.5)")
            action.add_argument("--music-seed", help="Melodi temasını bölümler arasında koru")
    args = cli.parse_args()
    if args.command == "voice":
        install(args.dir, args.piper)
    elif args.command in ("brief", "generate", "make"):
        previous = read_story(args.previous) if args.previous else None
        prompt = brief(args.idea, previous)
        if args.command == "make":
            if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
                raise ValueError(f"Yeni bölüm için boş bir hedef adı seç: {args.output}")
            if not args.model.is_dir() or not (args.model / "ses.onnx").is_file():
                raise ValueError("Önce voice komutuyla modeli kur veya --model ile yerel ses seç.")
            source = args.output / "bolum.json"
            generate(prompt, source, args.codex_model)
            print(f"Bölüm kaydedildi: {source}", flush=True)
            render(source, args.output / "video", args.model, 1.0, args.music_seed)
        elif args.command == "generate":
            generate(prompt, args.output, args.codex_model)
            print(args.output)
        else:
            print(prompt)
    elif args.command == "render":
        if not 0.7 <= args.pace <= 1.5:
            raise ValueError("--pace 0.7 ile 1.5 arasında olmalı")
        model = args.model or Path("models/seslen")
        if args.model is None and not model.exists() and read_story(args.story)["version"] == 1:
            model = Path("models") / MODEL
        render(args.story, args.output, model, args.pace, args.music_seed)
    else:
        data = read_story(args.story)
        if args.command == "preview":
            if not 1 <= args.shot <= len(data["shots"]):
                raise ValueError("Plan numarası aralık dışında")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            shot = data["shots"][args.shot-1]
            name = shot["board"]
            preview = compose(data, name, args.story.parent)
            if data["boards"][name].get("actors"):
                front = compose(data, name, args.story.parent, state="front")
                preview = draw_actors(data, data["boards"][name], preview, front, shot["lines"][0], 0.65, 0.45, 0)
            preview.save(args.output)
        print(f"{data['title']} · {len(data['shots'])} plan")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, ET.ParseError, subprocess.CalledProcessError, KeyError, TypeError) as error:
        sys.exit(f"OpenStoryTelling: {error}")
