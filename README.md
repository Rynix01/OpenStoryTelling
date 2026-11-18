# OpenStoryTelling

Türkçe bir hikâye fikrini resimli, seslendirilmiş dikey videoya dönüştürür. Codex hikâyeyi yazar, karakterleri çizer ve planları düzenler. Yerel derleyici Türkçe anlatımı, konuşmaya bağlı ağız hareketini, altyazıyı ve bölüm için kodla bestelenen müziği birleştirir.

**[Sarı Kaset filmini aç](examples/kiyi-radyo/video/film.mp4)** · [Senaryo ve 35 plan](examples/kiyi-radyo/bolum.json) · [Dört referans bölümün incelemesi](docs/referans-incelemesi.md)

| Örnek | Nasıl üretildi? |
|---|---|
| Sarı Kaset | Codex sohbetinde yazılan bir baba-kız hikâyesi. 13 özgün resim, kamera hareketleri, hatıra planları ve yerel seslendirme. [Çizimler ve üretim istemleri](examples/kiyi-radyo/gorseller.md) |
| Islak Bilet | İki planlık bir fikir gerçek Codex CLI oturumunda karakter ve dekor çizimlerine dönüştürüldü. Boyun, el-bilet yerleşimi ve yüz hareketleri sonradan düzenlendi. [Düzenlenebilir bölüm](examples/islak-bilet/bolum.json) · [Kısa filmi aç](examples/islak-bilet/video/film.mp4) |

## Codex sohbetinde kullan

Bu depoyu Codex'te açıp örneğin *“Son vapurda sahibini arayan bir anahtar hakkında iki dakikalık bir bölüm yap”* yaz. Depodaki [üretim talimatı](AGENTS.md) hikâyeyi, çizimleri, seslendirmeyi ve son video kontrolünü tarif eder. Hazır bölümü tekrar derlemek için yalnızca yerel araçlar gerekir. İkinci bölüm için önceki dosyayı göstererek aynı karakterlerle devam edebilirsin.

## Kurulum

Python 3.11–3.13, FFmpeg ve FFprobe gerekir. FFmpeg derlemesinde libx264, libass ve AAC bulunmalı. Aşağıdaki Windows komutlarını repo kökünde çalıştır. Bu çalışma alanındaki kopyada sanal ortam ve Türkçe model hazırdır; yeni klonda bu adımları uygula.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ost.py voice
```

Linux ve macOS'ta ortamı `python3 -m venv .venv` ile oluştur ve komutlarda `.venv/bin/python` kullan. Türkçe model ilk indirmede yaklaşık 63 MB yer kaplar. `voice` iki dosyanın SHA-256 özetini kontrol eder. [FFmpeg](https://ffmpeg.org/download.html) · [Piper](https://github.com/OHF-Voice/piper1-gpl)

## Fikirden videoya tek komut

Oturum açılmış Codex CLI ile aşağıdaki komut senaryoyu ve yeniden kullanılabilir vektör çizimlerini üretir. Ardından yerel TTS ve video derlemesi çalışır. `--codex-model` için kendi CLI oturumundaki bir modeli seçebilirsin. Buradaki model canlı üretimde doğrulandı. Bu seçeneği kaldırdığında CLI'ın varsayılanı veya `OPENSTORY_CODEX_MODEL` kullanılır.

```powershell
.\.venv\Scripts\python.exe ost.py make "Son vapurda unutulmuş bir anahtar, iki dakikalık bir gizem." --codex-model gpt-6.1-terra -o build/son-vapur
```

`build/son-vapur/bolum.json` düzenlenebilir kaynak, `video/film.mp4` ve `video/altyazi.srt` teslim dosyalarıdır. Derleme kesilirse kaydedilen JSON ile `render` komutunu çalıştır. Her yeni üretime ayrı bir hedef klasör ver.

## Bölümü düzenle veya devam ettir

```powershell
.\.venv\Scripts\python.exe ost.py check examples/kiyi-radyo/bolum.json
.\.venv\Scripts\python.exe ost.py preview examples/kiyi-radyo/bolum.json --shot 4 -o build/plan.png
.\.venv\Scripts\python.exe ost.py render examples/kiyi-radyo/bolum.json -o build/sari-kaset
.\.venv\Scripts\python.exe ost.py generate "Ertesi sabah vapur iskelesinde" --previous examples/islak-bilet/bolum.json --codex-model gpt-6.1-terra -o build/devam/bolum.json
```

`brief "fikir"` aynı yazım ve çizim tarifini açık sohbet için verir. `generate` yalnız bölüm kaynağını üretir. `--previous` isimleri, görsel kimlikleri, vektör çizimlerini ve hikâyenin kaldığı yeri yeni isteğe ekler. Resimli serilerde görsel referans için önceki bölümün WebP çizimlerini sohbette de kullanabilirsin.

`render --pace 1.10` konuşmayı yavaşlatır. `--music-seed "Kıyı Radyo"` bölümler arasında aynı müzik motifini korur. `--model yol/ses.onnx` başka bir yerel Piper sesi seçer ve yanında aynı adlı `.onnx.json` dosyasını bekler.

## Bölüm biçimi

| Alan | İçerik |
|---|---|
| `cast`, `continuity` | Karakter kimlikleri, önceki olayların sonucu ve açık kalan soru |
| `art` | Yeniden kullanılabilir SVG çizim parçaları. Gövde, aksesuar ve mimikler ayrı tutulabilir |
| `boards` | 720×1280 sahneler. Yerel PNG, JPEG veya WebP zemin ya da düz renk ve sıralı çizim katmanları |
| `layers` | Çizim adı, x/y, ölçek ve açı. `when: speaking` ses şiddetiyle açılan ağız, `when: blink` göz kapağı ekler |
| `shots` | Sahne adı, yaklaşan/sabit/uzaklaşan kamera ve seslendirilecek kısa replikler |

Piper her altyazı repliğini ayrı sentezler. Derleyici gerçek örnek sayılarından süreleri hesaplar ve plan sonlarını 30 fps kare sınırlarına hizalar. Nota dizisi, yumuşak ses zarfı ve konuşma sırasında müziği azaltan miks Python'da üretilir. FFmpeg, altyazıyı görüntüye işler ve 720×1280 H.264 / 48 kHz stereo AAC olarak dışa aktarır.

## Ücret ve ses modeli

Yerel seslendirme, beste, çizimlerin işlenmesi ve dışa aktarma ücretsiz çalışır. Hikâye yazımı mevcut Codex oturumunun erişim ve kullanım sınırlarına tabidir. Araç ChatGPT oturumuyla çalışır ve API anahtarı istemez. Yeni çizimler Codex'in yazdığı vektörlerle üretilebilir. Sarı Kaset'in hazır resimleri depoya dahildir.

Varsayılan Türkçe ses **tr_TR-dfki-medium**, 22.050 Hz, tek konuşmacılı bir Piper modelidir. Model kartında eğitim veri kümesi için **CC BY-NC-SA 4.0** belirtilir. Ticari bir yayın için kullanım amacına uygun lisanslı bir Piper modeli seç. [Ses modeli kartı](https://huggingface.co/rhasspy/piper-voices/blob/main/tr/tr_TR/dfki/medium/MODEL_CARD) · [DFKI Türkçe kayıtları](https://github.com/marytts/dfki-ot-data/) · [Lisans](https://creativecommons.org/licenses/by-nc-sa/4.0/)
