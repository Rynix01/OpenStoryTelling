"""Codex CLI is the author. Its only returned artifact is declarative JSON."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .story import validate


def brief(idea, previous=None):
    instructions = """Bir Türkçe dikey çizgi hikâye bölümü yaz ve çiz. Tek bir geçerli JSON nesnesi döndür.
İzleyiciyi ilk replikte somut bir merakla yakala. Eylem, tepki, nesne detayı ve kapanış kullan.
Birinci şahıs anlatıcı ve kısa doğal diyaloglar yaz. Kullanıcı süre vermediyse yaklaşık 2,5 dakika hedefle.
Aynı karakterin saçını, yüzünü ve kıyafetini her planda aynı art parçasından kur.
Çizimleri sen tasarla. SVG içeriğini JSON dizelerine yaz. Renkler, konturlar, yüz ifadesi,
eller, mekân ayrıntıları ve yakın/genel planlar için bilinçli seçimler yap. Harici dosya kullanma.
Şema örneği (gerçek bölümde bu çizim ve metinleri değiştir):
{"version":1,"title":"...","cast":{"isim":"görsel kimlik ve rol"},"continuity":"Sonraki bölüm için kalan soru ve durum",
"art":{"pencere":"<rect x='0' y='0' width='150' height='240' fill='#88b5ab'/>"},
"boards":{"oda":{"color":"#dfc99e","layers":[{"art":"pencere","x":120,"y":260,"scale":1,"angle":0}]}},
"shots":[{"board":"oda","camera":"push","lines":["..."]}]}
720×1280 koordinat alanı. art anahtarları ASCII harf, rakam, _ veya - kullanır.
SVG parçasında g,path,rect,circle,ellipse,line,polyline,polygon ve basit çizim nitelikleri kullanılabilir.
Metin, defs, href, stil sayfası ve url kullanma. Her pano için zemin ve sıralı katmanlar tanımla.
Konuşan yüzlerde ağzın açık halini üst katmana çiz ve bu katmana "when":"speaking" ekle.
Göz kapaklarını ayrı çizip "when":"blink" kullanabilirsin. Bu katmanlar sabit çizimin üstüne gelir.
Kamera push, pull veya hold. Her repliği tek altyazıda okunacak 3–12 kelimelik nefes gruplarına böl.
Her planın lines listesi o planda seslendirilecek sıralı metinleri içerir. Kaynak kod veya Markdown döndürme."""
    if previous:
        carry = {k: previous[k] for k in ("title", "cast", "continuity", "art")}
        instructions += "\nÖnceki bölümden devamlılık bilgisi ve yeniden kullanabileceğin çizimler:\n" + json.dumps(carry, ensure_ascii=False)
    return instructions + "\nBölüm isteği:\n" + idea


def generate(prompt, target, model=None):
    if target.exists():
        raise ValueError(f"Hedef zaten var: {target}")
    binary = shutil.which("codex.exe" if os.name == "nt" else "codex")
    if not binary:
        raise ValueError("Codex CLI bulunamadı. Mevcut sohbette brief komutunun çıktısını kullanabilirsin.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        answer = Path(tmp).resolve() / "answer.json"
        command = [binary, "exec", "-c", 'forced_login_method="chatgpt"', "-c", 'model_provider="openai"',
                   "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only"]
        if model:
            command.extend(["--model", model])
        command.extend(["--output-last-message", str(answer), "-"])
        env = {k: v for k, v in os.environ.items() if k not in {"OPENAI_API_KEY", "CODEX_API_KEY"}}
        subprocess.run(command, input=prompt.encode("utf-8"), env=env, cwd=tmp,
                       stdout=subprocess.DEVNULL, check=True)
        raw = answer.read_text(encoding="utf-8-sig").strip()
        if raw.startswith("```") and raw.endswith("```"):
            raw = raw.split("\n", 1)[1][:-3]
        data = json.loads(raw)
        validate(data, target.parent)
        with target.open("x", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
            out.write("\n")
