# OpenStoryTelling ile bölüm üretimi

Kullanıcı bir hikâye fikri verdiğinde bölümü bu sohbet içinde yaz ve çiz. Proje kökünden çalış. Kullanıcının dilini, süresini ve istediği görsel yönü uygula. Yalnız bir fikir verdiyse varsayılan format Türkçe, 9:16 ve yaklaşık iki buçuk dakikadır.

1. Devam bölümü için önceki bölümü oku. Karakterlerin kıyafetini ve çizim parçalarını koru. Her yeni karakterin yüzünü, siluetini, aksesuarını ve diğerleriyle ilişkisini belirle.
2. İlk cümlede merak uyandıran somut bir olay, ortada onu başka türlü okumamızı sağlayan bir ayrıntı ve finalde bir karşılık yaz. Her planın “lines” listesine altyazıda kolay okunacak nefes grupları koy. Tek konuşmacılı sesle diyaloğu anlaşılır kılacak anlatıcı geçişleri kullan.
3. Yeni bölüm için ayrı klasör ve bolum.json oluştur. Vektör örneği examples/islak-bilet/bolum.json içinde. Gövde, eller, kıyafet, eşya ve mekânı tekrar kullanılan SVG parçalarıyla çiz. Bakış, el hareketi, konuşan ağız ve göz kapağını duyguyla eşleştir. Resimli bir bölüm istenirse yerel çizimleri boards.file ile kullan. Önceki resimli bölümle devam ederken görselleri de incele.
4. Kurulu Python ile ost.py check ve ost.py preview çalıştır. Yüz, el, nesne ve altyazı alanlarını kontrol et. Yerel model eksikse ost.py voice ile kur. ost.py render ile filmi ve eşlik eden SRT dosyasını üret.
5. MP4'ün başlangıç, ortası ve sonundan kareleri kontrol et. FFprobe ile ses ve görüntü süresini, dikey çözünürlüğü ve ses kanalını doğrula. Kullanıcıya filmin, düzenlenebilir kaynağın ve gerekiyorsa yeni karakter çizimlerinin yolunu ver.

Aynı sohbette yazarken ikinci bir Codex çağrısı gerekmez. Terminalden tek komut istenirse ost.py make, adım adım kullanım için brief/generate/render vardır. Bu proje için ücretli bir API ekleme.
