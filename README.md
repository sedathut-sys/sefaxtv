# SefaXTV — Akıllı Web TV

**İzleyici: 0.9 · güncel imzalı katalog: v4 (6 laboratuvar kanalı / 25 kaynak).**

Kamusal GitHub Pages: https://sedathut-sys.github.io/sefaxtv/

Bu bir test prototipidir. Tüm kaynaklar kendi oluşturduğumuz `lab` görüntüleridir. Yetkisi doğrulanmamış üçüncü taraf spor veya TV yayını içermez. GitHub Pages **herkese açıktır**.

## Güven zinciri

- `index.html`: tek HTML izleyici, `CLIENT_BUILD=9`, eski `tv-lab-05` ile yeni `sefaxtv-7777dfd54f34cab3209c0080` **açık** anahtarlarını tanır.
- `catalog/latest.json`: P-256 ECDSA/SHA-256 imzalı, **v4** manifesti.
- `catalog/v4.json`: SHA-256 özeti manifestte sabitlenmiş, altıncı kanalı ekleyen tam katalog.
- `catalog/v3.json`: geriye uyumluluk için saklanan önceki doğrulanmış katalog.

**0.9/v4 yayın sırası tamamlandı:** Önce yeni açık anahtar izleyiciye eklendi ve GitHub Pages dağıtımı başarıyla tamamlandı. Sonra imzalı `v4.json` dağıtıldı ve doğrulandı. **En son** `latest.json` v4'e çevrildi. GitHub Actions her üç aşamanın dağıtımını da başarılı bildirdi. Eski v3 dosyaları değiştirilmedi.

İzleyici kataloğu yalnız **Güncelle** düğmesine basıldığında HTTPS üzerinden okur. ECDSA imzası, katalog SHA-256 özeti, şema/sürüm ve 20 kaynak sınırı kontrol edilir. Katalog/favori/geçmiş yerel IndexedDB'de yönetilir. Tarayıcı site verilerini temizlerse yerel kayıtlar kaybolabilir.

## Yönetici güvenliği

Yönetici HTML aracı, özel anahtar, parola, şifreli yedek ve GitHub erişim belirteci **bu halka açık depoda bulunmaz**. Özel imza anahtarı yönetici bilgisayarında üretildi; yönetici, yalnız `publicJwk` ve imzalı içerikten oluşan kamusal teslim paketini sağladı. Parola ve şifreli yedek yalnız yönetici tarafından saklanmalıdır.

GitHub'a yükleme/yayın yetkisi izleyici kodunda yoktur. Yönetici taslağının değiştirilmesi, tek başına merkezi kataloğu değiştirmez.

## Test ve sınırlamalar

- ECDSA P-256 64 bayt `r||s` imzası bağımsız Python cryptography ve Node WebCrypto ile doğrulandı.
- SHA-256 özet eşleşmesi, kaynak/kanal sınırları, v3 geriye uyumluluk, değiştirilmiş imza/veri ve bilinmeyen anahtar reddi kontrol edildi.
- GitHub Pages dağıtım işlemleri başarılı. Bu çalışma ortamında canlı HTTPS sitesine otomatik tarayıcı erişimi `ERR_BLOCKED_BY_ADMINISTRATOR` ile engellendi. Gerçek sitede Güncelle ve kalıcı IndexedDB davranışı tam uçtan uca doğrulanamadı.
- Yalnız deneysel görüntü üretimi; gerçek yayın sağlayıcı adaptörleri ve kullanım izinleri henüz eklenmedi.

## İleride yeni katalog sürümü

Yönetici, **aynı yerel imza anahtarının güvenli yedeğini** kullanarak monoton artan sürüm numarasıyla yeni paket imzalar. Önce yeni sürümlü katalog yüklenip doğrulanır; en son imzalı `latest.json` değiştirilir. Daha düşük sürüme dönülmez.
