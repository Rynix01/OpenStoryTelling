"""Codex CLI is the author. Its only returned artifact is declarative JSON."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .story import validate


def brief(idea, previous=None):
    instructions = """Türkçe bir dikey animasyon bölümü yaz. Sadece geçerli JSON döndür.
Bir tuhaflık, bir tepki ve karşılık kur. Referans temposu dakikada yaklaşık 100–108 sözcük.
Süre belirtilmediyse 2,5 dakika. Replikleri doğrudan karakterlere ver. Kadın/erkek yetişkin,
genç ve çocuk için ayrı Türkçe ses seç. Yeni karakter için çizim paleti ve oynayacağı hareketleri belirle.
Dekoru 720×1280 tam kadraj çiz. Hatira sahnesini geçmişte geçen hareketli bir plan olarak göster.
Albüm sayfası, çerçeve, paspartu, başlık şeridi veya slayt tasarlama.
Aşağıdaki biçim örneğidir. Kendi olayını, oyuncularını, paletini, dekorunu ve planlarını oluştur.
{"version":2,"title":"...","cast":{"Ela":"Kız çocuk, sekiz yaş"},"voices":{"Ela":"elif"},
"continuity":"...","puppets":{"Ela":{"role":"girl","child":true,"hair":"braid","hair_color":"#503732","skin":"#e9b68d",
"coat":"#bd8051","trim":"#f2d599","pants":"#58636a"}},
"art":{"pencere":"<rect x='70' y='120' width='325' height='405' fill='#aacbc5'/>"},
"boards":{"oda":{"color":"#e2cbb0","layers":[{"art":"pencere"}],"actors":[{"id":"Ela","x":310,"y":430,
"scale":2.15,"face":"right","gesture":"heart","emotion":"merak"}]}},
"shots":[{"board":"oda","camera":"hold","lines":[{"speaker":"Ela","emotion":"merak","gesture":"point","text":"Peki bunu buraya kim bıraktı?"}]}]}
Sahne planlarında actors kullan. x ve y yüzün ortasıdır. 1 ölçek yetişkinin ayaklarını yüzden 374 birim
aşağı getirir. Genel planda ölçeği 1.3–1.6, yakın planda 2.4–3.0 civarında tut. Birbirine bakan
oyuncuları karşılıklı konumlandır. Konuşanı ve dinleyenin tepkisini ayrı ayrı yönet.
hair: bob, wave, crop, silver veya braid. face: left veya right. Oyuncu elde cassette, mic veya wire
tutuyorsa prop alanı ekle. Başka bir elde tutulan eşyayı art içinde tutma noktası (0,0) olacak
şekilde yaklaşık 30 birim boyunda çiz ve oyuncuda propArt ile bu çizime bağla.
Her oyuncuda role alanı woman, man, girl (kız çocuk) veya boy (erkek çocuk) olsun.
Sesler: kadın nehir/selin/ayse, erkek ege/serdar, genç kız zeynep, genç erkek emre, kız çocuk elif,
erkek çocuk can, yaşlı kadın fatma, yaşlı erkek hasan. Aynı karakter hep aynı sesi kullanır.
Her replikte speaker, text (1–24 kelime) ve emotion gerekli. Duygular notr, merak, neseli, heyecan,
uzgun, ozur, fisilti, uyari, kizgin. İsteğe bağlı intensity 0–1, pause 0–4 saniye, speed 0.7–1.35.
Mode dialogue, iç ses için thought, kayıttan gelen ses için recording. Hareketler rest, reach, offer,
heart, listen, point, press, wipe, wave, recoil, clap. Kamera hold, push, pull. Dinleyenin duygusunu ve
hareketini sahnede tanımla. Vektör dekorunda g/path/rect/circle/ellipse/line/polyline/polygon ve
temel SVG çizim nitelikleri kullan; dış dosya, metin, defs, href, style ve url kullanma. Katman
yerleşimi art, x, y, scale ve angle alır. Önde kalacak masa gibi katmana when: front ekle."""
    if previous:
        carry = {k: previous[k] for k in ("title", "cast", "continuity", "art", "puppets", "voices") if k in previous}
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
        if data["version"] != 2:
            raise ValueError("Yeni bölümlerde karakter seslerini içeren version 2 gerekli.")
        with target.open("x", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
            out.write("\n")
