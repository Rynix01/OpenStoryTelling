# Dört bölümün kurgu notları

Dört yerel MP4'ün tamamını dört saniye aralıklarla örnekledik. Görüntüyü FFprobe ile ölçtük. FFmpeg'de 180×320 önizleme üzerinde 0,17 sahne değişimi eşiğini ve sesin tamamında EBU R128 ölçümünü kullandık. Aşağıdaki sayılar belirgin görüntü değişimlerini gösterir. Yakınlaşma, ışık geçişi ve peş peşe kesmeler bu sayıyı etkileyebilir.

| Bölüm | Süre | Eşiği geçen değişim | Ortanca plan aralığı | Bütünleşik ses | Dinamik aralık | Gerçek tepe |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 2:47,42 | 58 | 2,70 sn | −14,2 LUFS | 4,2 LU | −0,3 dBTP |
| 2 | 2:48,92 | 41 | 3,63 sn | −14,1 LUFS | 4,0 LU | −1,4 dBTP |
| 3 | 2:27,41 | 34 | 4,10 sn | −14,2 LUFS | 3,6 LU | −1,3 dBTP |
| 4 | 2:41,11 | 32 | 4,50 sn | −14,2 LUFS | 3,1 LU | −1,7 dBTP |

Ortak teslim formatı 720×1280, 9:16, 30 fps, H.264 görüntü ve 48 kHz stereo AAC ses. Ölçümler bitmiş mikse ait. Konuşmanın ve müziğin ayrı seviyeleri ile kullanılan TTS motoru bu değerlerden çıkarılamaz.

## Bölümler nasıl ilerliyor?

**Bölüm 1.** İlk yarım dakikada koltuktaki adamın yüzü ile anne ve çocuğun tedirgin tepkileri arasında gidip geliyoruz. Duvardaki sahne afişine kesme, Aslı'nın geçmişini bir nesne üzerinden anlatıyor. Yaklaşık 1:24'te renkler soğuyor ve yatak odasının eşiği aile üyeleri arasındaki mesafeyi gösteriyor. Sabah ışığına geçişle kahvaltı, gitar ve alışveriş torbaları görünüyor. Karakterdeki değişimi yüzlerdeki tepki ve ev işleri üzerinden okuyoruz.

**Bölüm 2.** Kahvaltı hazırlayan adam ve onu mutfaktan izleyen Aslı ilk karşılıklı planları oluşturuyor. Yaklaşık birinci dakikada telefon ekranına kesilerek karakterin araştırması görünür hale geliyor. İkinci yarıda gitarı çalan adamla onu duyanların yüzleri dönüşümlü gösteriliyor. Tek renkli kısa anı planı, bugünkü davranışın geçmişle ilişkisini kuruyor. Son kısımda telefon ve kapı, dikkati kadrajın dışına taşıyor.

**Bölüm 3.** Telefonla başlayan bölümde çamaşırların yanındaki iki kişilik genel plan, birinden izin istemek gibi küçük bir davranışı görünür kılıyor. Elde tutulan çamaşır, geri çekilen el ve yüzünü kapatan Aslı aynı karşılaşmayı farklı ölçeklerde anlatıyor. Sofra ve koltuktaki bebek resmi, çocuğun isteğini bölümün ikinci yarısına taşıyor. Loş yatak odasından sabah masasına geçiş zaman atlamasını kuruyor. Kapı aralığından görünen çocuk sonraki bölüme bağlanıyor.

**Bölüm 4.** Bebekle ilgili konuşmada Nil, babasının tepkisi ve iki kişilik genel plan birbirini izliyor. Yaklaşık 0:52'de evden koşu parkuruna geçiliyor. Yeşil ağaç sırası ve koyu spor kıyafeti, önceki üç bölümün ev paletinden hemen ayrılıyor. Ardından telefon, mutfak, yumurta ve sofra gibi tanıdık ayrıntılarla eve dönülüyor. Kapanışlarda görülen açık kâğıt zemin ve çocuk çizimi serinin tanınmasını sağlıyor.

## Üretim kararları

- İlk cümlede karakterin fark ettiği somut bir tuhaflık ver. Sonraki planda onu kimin gördüğünü göster.
- Yüzü ve elleri üst ve orta alanda okunur tut. Referanslarda kısa, açık renk, koyu kenarlı altyazı çoğunlukla görüntü yüksekliğinin yaklaşık yüzde yetmişinde. Uzun metni nefes gruplarına ayır.
- Genel plan mekânı tanıtsın. Yakın plan yeni bir bilgi versin. Bir eşya önce ipucu, sonra cevap olarak tekrar görünebilir.
- Aynı saç, kıyafet ve aksesuarları koru. Gece-gündüz veya hatıra geçişini ışık ve paletle anlat. Bakış, el hareketi ve kadraj değişimi sınırlı animasyonu taşır.
- Müzik için seyrek notalı, yumuşak girişli özgün bir motif üret. Konuşma sırasında geri çek ve son cümleden sonra kısa bir çözülme bırak. Bu, araç için bir beste tercihidir.
- Örnek bölüm kendi karakterlerini, mekânını ve görsel kapanışını kullanır. Kaynak videolar kullanıcıya ait yerel inceleme girdileridir.
