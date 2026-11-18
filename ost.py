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


def main():
    cli = argparse.ArgumentParser(description="OpenStoryTelling · Türkçe çizgi hikâye atölyesi")
    sub = cli.add_subparsers(dest="command", required=True)
    voice = sub.add_parser("voice", help="Türkçe Piper modelini indir veya doğrula")
    voice.add_argument("--dir", type=Path, default=Path("models"))
    for name in ("brief", "generate", "make"):
        author = sub.add_parser(name, help={"brief":"Sohbet için bölüm isteği hazırla", "generate":"Codex CLI ile bölüm yaz ve çiz", "make":"Fikirden proje ve MP4 üret"}[name])
        author.add_argument("idea")
        author.add_argument("--previous", type=Path)
        if name in ("generate", "make"):
            author.add_argument("-o", "--output", type=Path, required=True)
            author.add_argument("--codex-model", default=os.environ.get("OPENSTORY_CODEX_MODEL"), help="Codex CLI oturumunda kullanılabilen model")
        if name == "make":
            author.add_argument("--model", type=Path, default=Path("models") / MODEL)
            author.add_argument("--music-seed")
    for name in ("check", "preview", "render"):
        action = sub.add_parser(name, help={"check":"Bölüm dosyasını doğrula", "preview":"Bir planı PNG olarak çiz", "render":"Seslendir ve MP4 üret"}[name])
        action.add_argument("story", type=Path)
        if name != "check":
            action.add_argument("-o", "--output", type=Path, required=True)
        if name == "preview":
            action.add_argument("--shot", type=int, default=1)
        if name == "render":
            action.add_argument("--model", type=Path, default=Path("models") / MODEL)
            action.add_argument("--pace", type=float, default=1.0, help="Piper süre çarpanı (0.7–1.5)")
            action.add_argument("--music-seed", help="Melodi temasını bölümler arasında koru")
    args = cli.parse_args()
    if args.command == "voice":
        install(args.dir)
    elif args.command in ("brief", "generate", "make"):
        previous = read_story(args.previous) if args.previous else None
        prompt = brief(args.idea, previous)
        if args.command == "make":
            if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
                raise ValueError(f"Yeni bölüm için boş bir hedef adı seç: {args.output}")
            if not args.model.is_file() or not args.model.with_suffix(".onnx.json").is_file():
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
        render(args.story, args.output, args.model, args.pace, args.music_seed)
    else:
        data = read_story(args.story)
        if args.command == "preview":
            if not 1 <= args.shot <= len(data["shots"]):
                raise ValueError("Plan numarası aralık dışında")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            compose(data, data["shots"][args.shot-1]["board"], args.story.parent).save(args.output)
        print(f"{data['title']} · {len(data['shots'])} plan")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, ET.ParseError, subprocess.CalledProcessError, KeyError, TypeError) as error:
        sys.exit(f"OpenStoryTelling: {error}")
