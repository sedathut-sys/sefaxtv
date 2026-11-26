# SeFaTV — Proje Durum Belgesi

Son güncelleme: 26 Kasım 2026 (Türkiye)
Politika sahibi: Kullanıcı
Durum: Aktif, tüm geliştirmelerde uygulanacak.

## AKILLI VE VERİMLİ GELİŞTİRME POLİTİKASI

Bundan sonraki bütün geliştirmelerde aşağıdaki kuralları kalıcı olarak uygula:

- Yüksek akıl yürütme, kod kalitesi ve mühendislik standartlarını koru.
- Gereksiz araştırma, tekrar, test ve mikro düzeltmelerle zaman kaybetme.
- Oyuncunun veya kullanıcının gerçekten fark edeceği geliştirmelere öncelik ver.
- Küçük değişikliklerde yalnızca ilgili hedefli testleri çalıştır.
- Kapsamlı testleri ana geliştirme aşamalarının sonunda veya ciddi teknik risk oluştuğunda gerçekleştir.
- Daha önce doğrulanmış ve değişmemiş bileşenleri gereksiz yere tekrar test etme.
- Önbellekleri, mevcut test kanıtlarını ve başarılı önceki sonuçları akıllıca kullan.
- Küçük kusurları mümkün olduğunca tek geliştirme paketinde gider.
- Ciddi fayda sağlamayan mükemmelleştirme çalışmalarını durdur.
- Onaylanmış bileşenleri gereksiz yere yeniden geliştirme.
- Güvenlik, performans ve temel işlevlerden taviz verme.
- Geliştirme süresi ile elde edilen kalite kazanımını karşılaştır.
- Sonraki en faydalı geliştirme aşamasını kendin belirle.
- Mevcut görsel onay kurallarını koru.
- Bu politikayı proje durum belgesine kaydet ve sonraki bütün işlemlerde uygula.

Her işlemin sonunda yapılan geliştirmeyi, test sonuçlarını, kalite puanını ve sıradaki işlemi kısa şekilde bildir. Devam et butonunu ekle.

**Temel ilke: Maksimum zekâ, maksimum kalite, minimum gereksiz işlem.**

## Uygulama düzeni

- Her yeni geliştirme oturumunda bu belgeyi esas al; en güncel kanıt ve ilgili önceki kayıtları kullan.
- Test kapsamını değişen bileşenler ve bağımlılık risklerine göre seç. Değişmeyen doğrulanmış bileşenleri sırf yeni sürüm numarası için tekrar sınama. Ana aşama sonunda veya ciddi riskte kapsamlı regresyon testi yap.
- Hata düzeltmelerini ve kullanıcıya fayda sağlayan işleri mümkün olduğunca tek anlamlı pakette birleştir.
- Kalite puanı 10 üzerinden, ilgili aşamanın doğrulanmış işlev, doğruluk, kararlılık, performans ve kullanıcı deneyimi kanıtlarına göre gerekçeli değerlendirme olarak verilir; ölçülmemiş kaliteyi ölçülmüş gibi sunma. Kanıt yetersizse puan geçici veya henüz ölçülmedi olarak işaretlenir. Kalite puanı PASS ya da kullanıcı kabulü yerine geçmez.
- Kırmızı Bülten kuralı aynen yürürlükte: gerçek uygulama PASS ve açık kullanıcı kabulü olmadan Kırmızı Bülten yok. Görsel onay, 0 TL zorunlu servis gideri, ortak HTML önceliği ve onaylanmış kodu koruma kuralları değişmez.
- Sadece belge değişikliklerinde belge içeriğini ve değişiklik kapsamını kontrol et; çalışma kodunu yeniden test etme.

## Güncel durum — 26 Kasım 2026

| Bileşen | Durum | Kanıt |
|---|---|---|
| 0.26 gerçek TV (Bir Gün TV) | Kullanıcı görüntü ve ses PASS | https://sedathut-sys.github.io/sefaxtv/live-tv-test/ ; 0.26 dalı research/TEST_KULLANICI_026_GERCEK_TV.md |
| 0.28 akıllı HLS izleyici | Otomatik PASS; ayrı geliştirme dalı | https://github.com/sedathut-sys/sefaxtv/actions/runs/45882873337 ; 30.2988 sn, 757 kare |
| 0.30 yerel dublaj motoru | 8/8 teknik eşikler PASS; 7 sentetik + 1 arşiv insan konuşması | https://github.com/sedathut-sys/sefaxtv/actions/runs/45885170590 ; Whisper Small.en, OPUS-MT, Piper Fahrettin; RTF .5015 |
| 0.31 kontrollü gerçek zamanlı HLS dublaj | Otomatik PASS; 4/4 dublaj, kasıtlı gecikmede orijinal ses, 21.333 ms akış zaman damgası farkı | https://github.com/sedathut-sys/sefaxtv/actions/runs/45886230299 |
| 0.32 harici kaynak | HTTP 404; canlı dublaj testi başlamadı | https://github.com/sedathut-sys/sefaxtv/actions/runs/45886717311 |
| 0.33 yerel HLS paketi | Hedefli paket PASS; harici gerçek yayın doğrulanmadı | https://github.com/sedathut-sys/sefaxtv/actions/runs/45887331592 |
| 0.34 izinli tarayıcı sekmesi yaklaşımı | Kod ve derleme kontrolleri PASS; bütünleşik test çalışıyor (son kontrol) | https://github.com/sedathut-sys/sefaxtv/actions/runs/45888214652 |

0.30 ses doğallığı kullanıcı kabulü yok. 0.31 senkron altyapısı geçici 8/10; gerçek kullanıcı gecikmesi ve dudak senkronu ölçülmedi. 0.34 test kontrollü canvas/ses MediaStream üzerinden yapılır, gerçek ekran paylaşımı izin penceresi ve canlı TV ayrı kullanıcı testi gerektirir. 0.34 paket kalite puanı henüz ölçülmedi. Windows paketi Python 3.11 ve FFmpeg/ffprobe PATH gerektirir; ilk çalıştırmada model indirmeleri. Ana uygulama ve 0.26 kullanıcı sayfası değişmedi. Kırmızı Bülten yok.

Sıradaki iş: 0.34 tamamlanmış CI sonucunu ve artifact varlığını kontrol et; bütünleşik test PASS ve paket mevcutsa kullanıcıya kısa, gerçek izinli İngilizce yayın sekmesi testi sun. FAIL ise yalnız ilgili arızayı gider. Önceki başarılı TV/ASR/TTS testlerini gereksiz yere tekrar etme.
