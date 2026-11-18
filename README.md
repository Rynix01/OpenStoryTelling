# OpenStoryTelling

Codex Türkçe hikâyeyi yazar, karakterleri çizer ve oynatır. Yerel derleyici kadın, erkek ve çocuk rollerini ayrı seslerle okur, sahnedeki oyuncuyu repliğe göre hareket ettirir, sakin bir melodi besteler ve altyazılı dikey MP4 üretir.

**[Sarı Kaset'i izle](examples/kiyi-radyo/video/film.mp4)** · [Senaryo ve oyuncular](examples/kiyi-radyo/bolum.json) · [Dekorlar](examples/kiyi-radyo/gorseller.md) · [Dört referansın incelemesi](docs/referans-incelemesi.md)

[Dört sesi aynı sahne dizisinde dinle](examples/kiyi-radyo/video/kisa-sahne.mp4) · [Kayıp Anahtar, kız çocuk ve baba diyaloğu](examples/kayip-anahtar/video/film.mp4)

Sarı Kaset'te yetişkin Ece ve Selim'i Nehir ve Serdar, kasetteki dokuz yaşındaki Selim'i Can, annesi Nermin'i Ayşe seslendirir. Sesler yapay zekâ ile üretilmiştir. 28 planda el-kol hareketleri, göz-kaş tepkileri, baş eğimi ve konuşma sırasında ağız açıklığı zaman içinde değişir. İki kişilik planlarda dinleyen karakterin kendi tepkisi vardır.

## Codex sohbetinde

Depoyu Codex'te açıp *“Son vapurda annesine bir sır söylemek isteyen çocuk hakkında iki dakikalık bir bölüm yap”* yaz. Yazım ve çizim mevcut Codex oturumunu kullanır. Kurulumdan sonra seslendirme, animasyon, müzik ve video derlemesi bilgisayarda çalışır. [Üretim talimatı](AGENTS.md)

## Kurulum

Python 3.11–3.13 ve libass, libx264, AAC destekli FFmpeg kurulu olmalı. Windows'ta repo kökünde şu komutları çalıştır.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ost.py voice
```

Linux ve macOS'ta sanal ortam için `python3 -m venv .venv`, komutlar için `.venv/bin/python` kullan. Seslen'in yaklaşık 326 MB büyüklüğündeki beş model dosyası sabit sürümden indirilir ve özetleri doğrulanır. [FFmpeg](https://ffmpeg.org/download.html) · [Seslen TTS](https://github.com/seslen-tr/seslen-tts)

## Fikirden filme

```powershell
.\.venv\Scripts\python.exe ost.py make "Kayıp anahtarı bulan küçük kız babasına seslenir, iki dakikalık bir bölüm." --codex-model gpt-6.1-terra -o build/anahtar
```

`--codex-model` ile oturumunda kullanılabilen modeli seç. Seçeneği kaldırırsan CLI varsayılanı veya `OPENSTORY_CODEX_MODEL` kullanılır. Yeni klasörde düzenlenebilir `bolum.json` ve `video` altında film, SRT ve zaman damgalı `seslendirme.json` yer alır.

```powershell
.\.venv\Scripts\python.exe ost.py check examples/kiyi-radyo/bolum.json
.\.venv\Scripts\python.exe ost.py preview examples/kiyi-radyo/bolum.json --shot 8 -o build/plan.png
.\.venv\Scripts\python.exe ost.py render examples/kiyi-radyo/bolum.json -o build/sari-kaset
.\.venv\Scripts\python.exe ost.py generate "Ertesi sabah" --previous examples/kiyi-radyo/bolum.json --codex-model gpt-6.1-terra -o build/devam/bolum.json
```

`brief` açık sohbet için çizim ve yönetim tarifini verir. `--previous` karakterleri, ses dağılımını, çizim paletini ve öykünün devam bilgisini taşır. `--pace` genel konuşma temposunu, `--music-seed` müziğin motifini belirler. Her yeni çıktıya ayrı klasör ver.

## Bir repliği yönet

```json
{"speaker":"KucukSelim","text":"Anne, şimdi konuşursam bütün mahalle duyar mı?","emotion":"merak","intensity":0.85,"gesture":"heart","pause":0.4}
```

| Alan | Kullanım |
|---|---|
| `voices` | Karakter → ses. Örneğin kız çocuk için `elif`, erkek çocuk için `can`, yetişkin kadın için `nehir` veya `ayse`, yetişkin erkek için `serdar` veya `ege`. |
| `emotion` | `merak`, `heyecan`, `uzgun`, `ozur`, `fisilti`, `uyari`, `kizgin`, `neseli` ve `notr`. `intensity` duygu şiddetini, `speed` replik hızını ayarlar. |
| `mode` | `dialogue` konuşanı oynatır. `thought` ve `recording` sahnedeki ağızları sessiz tutar. |
| `puppets`, `boards.actors` | Saç, ten, giysi ve yaşla karakteri oluştur. `role` ile ses eşleşmesini denetle. Yüz merkezini x/y ile, yönü face ile, davranışı gesture ve emotion ile belirle. Elde tutulan kaset, mikrofon ve kablo bileği izler. Özel çizimi ele bağlamak için `propArt` kullan. |
| `art`, `layers` | SVG dekoru ve aksesuarlar. `when: front` masa gibi parçaları karakterin önüne getirir. Yerel PNG, JPEG ve WebP sahne zemini olarak kullanılabilir. |

Konuşma zamanları sentezlenen sesin gerçek süresinden alınır. Oyuncular saniyede 15 ayrı pozla çizilir. FFmpeg bunları 720×1280, 30 fps H.264 ve 48 kHz stereo AAC olarak birleştirir. Ağız açıklığı sesteki enerjiye dayanır. Jestler senaryoda seçilen eklem hareketleridir.

## Ücret ve lisans

Yeni bölümlerde ücretli TTS servisi veya API anahtarı gerekmez. Seslen TTS kodu MIT, model ağırlıkları ve sesleri CC BY-SA 4.0 kapsamında yayımlanır. Seslerin yapay zekâ ile üretildiğini yayın açıklamasında belirt. [Model ve kullanım koşulları](https://huggingface.co/seslen-tr/seslen-tts)

Eski tek anlatıcılı bölüm biçimi de okunur. İlk sürümün [Islak Bilet örneği](examples/islak-bilet/bolum.json) ve [filmi](examples/islak-bilet/video/film.mp4) bu biçimdedir. Orijinal Piper sesini kullanmak için `voice --piper`, ardından `render ... --model models/tr_TR-dfki-medium.onnx` çalıştır. DFKI veri kümesi için model kartı CC BY-NC-SA 4.0 belirtir. [Piper ses kartı](https://huggingface.co/rhasspy/piper-voices/blob/main/tr/tr_TR/dfki/medium/MODEL_CARD)
