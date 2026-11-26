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
| 0.26 gerçek TV test sayfası (Bir Gün TV) | Kullanıcı görüntü ve ses PASS | https://sedathut-sys.github.io/sefaxtv/live-tv-test/ ; kullanıcı bildirimi research/TEST_KULLANICI_026_GERCEK_TV.md (0.26 dalı) |
| 0.28 akıllı HLS izleyici | Otomatik PASS; ayrı geliştirme dalı | https://github.com/sedathut-sys/sefaxtv/actions/runs/45882873337 ; 30.2988 sn, 757 kare |
| İngilizce ASR | Base.en geçici aday; 4 sentetik örnekte WER 0 | 0.28 aynı test; gerçek spiker doğruluğu henüz ölçülmedi |
| Türkçe çeviri | Argos spor terimleri başarısız; 0.29 OPUS-MT ve M2M100 karşılaştırması hazırlanmış | lab/sefaxtv-pilot-v029, f881754576babc14fce28cc34fcd436568d64e73 |
| Türkçe ses | eSpeak NG WAV üretimi doğrulandı; doğallık, canlı dublaj ve senkronizasyon doğrulanmadı | 0.27 ve 0.28 kayıtları |

Sıradaki iş: 0.29 çeviri sonuçlarını incele; kaliteye en fazla katkı sağlayan sonraki geliştirme paketini seç. Değişmeyen TV oynatıcıya gereksiz tekrar testi çalıştırma. Başarılı 0.26 kullanıcı test sayfasını ve ana uygulamayı koru. Doğal Türkçe dublaj ve gerçek zamanlama ölçümlerini kullanıcıya gösterilebilir bir aşamada birleştir. Kullanıcıya hazır olmayan sonucu başarılı diye sunma.
