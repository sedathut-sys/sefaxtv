# SefaXTV — Akıllı Web TV

**Kamuya açık test sürümü: 0.8 (tek HTML).**
Yayın: https://sedathut-sys.github.io/sefaxtv/

Bu depo sadece kendi laboratuvar görüntümüzü oynatır; resmî yayıncı izinleri doğrulanmadan gerçek TV veya spor yayını içermez. GitHub Pages web sitesi **herkese açıktır**.

## Güncelle ve imza güvenliği

- `index.html`: yalnız izleyici. Katalog yalnız kullanıcı **Güncelle** düğmesine bastığında HTTPS üzerinden indirilir.
- `catalog/latest.json`: imzalı manifest (P-256 ECDSA/SHA-256; ham UTF-8 manifest baytları base64url içinde).
- `catalog/v3.json`: mevcut canlı imzalı test kataloğu. **0.8 geçişinde değiştirilmedi.**
- Veriler ve favoriler izleyicinin IndexedDB'sinde saklanır. Yönetici parolası, GitHub tokenı veya özel imza anahtarı izleyiciye konulmaz.

## 0.8 — yönetici/yayın protokolü

Yerel yönetici imzalama HTML'i **bu public depoda BULUNMAZ**. Yerel araç kategori/kanal taslağını hazırlar. Yeni P-256 özel anahtarı yönetici bilgisayarında üretir; **PBKDF2-SHA256 (600.000 iterasyon) + AES-256-GCM** ile şifrelenmiş PKCS#8 yedeğini sadece yöneticiye indirir. Parola ayrı saklanır. Bellekte kullanılan özel CryptoKey dışa aktarılamaz; sayfa kapandığında dosya yedeği olmadan tekrar açılamaz.

**İki aşamalı güvenli yayın:**

1. Yönetici anahtarını yerel aracında üretir, **şifreli yedeğini ve parolasını güvenle saklar**; yalnızca `keyId` ve açık JWK anahtarını yetkili yayıncıya verir.
2. Yeni **açık** anahtarı `index.html` içindeki `TRUSTED_PUBLIC_KEYS` listesine ekleriz. GitHub Pages dağıtımının başarılı olduğunu doğrularız. Eski `tv-lab-05` anahtarı ve çalışan v3 aynen kalır.
3. Yönetici, v4 taslağını doğrulayıp özel anahtarla `v4.json` ve `latest.json` üretir. Aracın çıktısı iki ayrı dosyadır; şifreli yedek **asla yayın dosyası değildir**.
4. Yetkili GitHub hesabıyla **önce** `catalog/v4.json` dosyasını yükler, yayımlanmış dosyanın bayt özetini doğrularız. **En son** `catalog/latest.json` dosyasını değiştiririz. `latest` yüklenene dek eski imzalı v3 günceldir.
5. Yeni pakette hata varsa eski sürüme işaret eden manifesti geri koymayız. En son sağlam içerikle **daha yüksek sürüm numarası** imzalarız. GitHub'ın site dağıtım geçmişini kontrol ederiz.

**Yayın ayrılığı:** Bu depo yalnız izleyici ve kamusal JSON kataloğudur. Özel anahtar, anahtar yedeği, imzasız taslak, yönetici HTML'i ve GitHub erişim belirteci bu depoya yüklenmez. Yönetici HTML'i ağ isteği veya GitHub API çağrısı yapmaz; yetkilendirilmiş GitHub yayımlaması ayrı işlemdir.

**Mevcut durum:** 0.8 izleyicinin çoklu açık anahtar doğrulama yapısı hazır, ancak yeni yöneticinin açık anahtarı henüz üretilmediği için güven listesinde yalnız v3'ün `tv-lab-05` anahtarı bulunuyor. Bu nedenle yeni v4 **henüz yayımlanmadı**.

## Kontroller

- ECDSA oluşturma, doğrulama, yanlış parola, değiştirilmiş içerik, SHA-256 ve 20 kaynak sınırı otomatik test edildi.
- Tek HTML izleyici ve yerel yönetici formu Chromium'da temel UI testinden geçti.
- GitHub Pages yayımlama işinin durumu GitHub Actions üzerinden kontrol edilir. Gerçek canlı HTTPS + IndexedDB uçtan uca tarayıcı testi ayrıca gereklidir.
