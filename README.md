# SefaXTV — Akıllı Web TV

**Güncel kamuya açık laboratuvar sürümü: 0.7.** Yalnız kendi ürettiğimiz test videosu; gerçek TV veya spor yayını içermiyor.

Yayın adresi: https://sedathut-sys.github.io/sefaxtv/

## İzleyici sitesi

- `index.html`: tek HTML (CSS ve JS içeride). Arama, kategori, tarayıcıya özgü favoriler ve doğrulanmış oynatma kapağı.
- `catalog/latest.json`: WebCrypto ECDSA P-256 ile imzalı manifest.
- `catalog/v3.json`: yayınlanan son **imzalı** test kataloğu. 0.7 arayüzü bu v3 dosyasıyla geriye uyumlu.
- `Güncelle` düğmesi dışarıdan imzalı katalog alır; yönetim yetkisi vermez.

## Güvenlik / yönetici

GitHub Pages ve kaynak dosyaları **herkese açık**. İzleyici uygulamasında parola, özel anahtar, GitHub tokenı veya yönetici düzenleme ekranı bulunmaz.

Yöneticiye ait v0.7 HTML taslak düzenleyicisi **kamu deposuna yüklenmez**; yalnız yerel bilgisayarda tutulur. Kategori, kanal ve en çok 20 laboratuvar kaynağını düzenleyip **imzasız taslak** dışa aktarabilir. Taslak katalogların yayımlanabilmesi için sonraki aşamada yerel imzalama ve GitHub yetkili yayın akışı gerekir.

Resmî sağlayıcı ve yayın izinleri doğrulanmadan hiçbir üçüncü taraf kaynak eklenmez. Mevcut `lab` sağlayıcısı yalnız öz üretim test görüntüsünü gösterir.

## Durum

- GitHub Pages dağıtımı doğrulandı.
- ECDSA imza, SHA-256, şema ve kötü paket reddi otomatik test edildi.
- Chromium ortamında arama, kategori, favori ve yerel düzenleyici kontrolleri geçti.
- IndexedDB yükseltmesi ve favori koruma mantığı simüle edildi. Gerçek tarayıcıda canlı siteye erişim/kayıt kalıcılığı ayrı kabul testidir.
