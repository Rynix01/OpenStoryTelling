# OpenStoryTelling ile bölüm üretimi

Kullanıcı bir fikir verdiğinde hikâyeyi bu sohbet içinde yaz ve tam ekran 9:16 bir bölüm olarak üret. Varsayılan dil Türkçe, hedef süre yaklaşık iki buçuk dakikadır. Örnek proje examples/kiyi-radyo/bolum.json içinde.

1. Yeni bölümler için version 2 kullan. Her konuşmacının yaşına ve rolüne uygun ayrı bir Türkçe ses seç. Replikte speaker, emotion ve text ver. Heyecan, merak, özür ve üzüntünün ses şiddeti ve duraklamasına sahneye göre karar ver. Devam bölümünde önceki ses ve çizim kimliklerini koru.
2. Karakterleri ilk cümleden itibaren sahnede oynat. Dekoru kenardan kenara doldur. İç sesi thought, banttan gelen sahne dışı sesi recording olarak işaretle. Hatırayı oyuncuların içinde yaşadığı bir sahneye keserek göster. Diyalogda bakış, kaş, ağız ve el hareketini, ayrıca dinleyicinin tepkisini yönet.
3. Her yeni bölüm için ayrı klasör oluştur. Kodla çizilen aktörleri puppets ve boards.actors ile kur. Tutulan küçük eşyayı ele bağla. Gerekirse dekoru SVG veya yerel WebP olarak ekle. Bölümün içine albüm sayfası, yazılı hatıra kartı veya dekoratif başlık şeridi koyma.
4. ost.py check ve ost.py preview ile sahneyi kontrol et. ost.py voice ücretsiz Türkçe Seslen modelini kurar. ost.py render ile MP4, altyazı ve seslendirme dökümünü üret. Sohbet içindeki üretim için ikinci bir Codex oturumu gerekmez.
5. Teslimden önce birden fazla rolün karşılıklı konuştuğu anı ve sessiz tepkiyi kontrol et. FFprobe ile görüntü ve ses süresini doğrula. Kullanıcıya izlenebilir filmi ve gerektiğinde kısa karşılaştırma örneğini ver. Seslerin yapay zekâyla üretildiğini belirt.
