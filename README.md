# SefaXTV — Akıllı Web TV

Bu depo, yalnız kendi ürettiğimiz test görüntüsüyle çalışan **0.6 laboratuvar sürümünün** GitHub Pages yayın alanıdır. Gerçek TV veya üçüncü taraf spor yayınları içermez.

## GitHub Pages

Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/(root)` → Save.

Yayın adresi: https://sedathut-sys.github.io/sefaxtv/

## Dosyalar

- `index.html`: tek HTML içinde arayüz ve test oynatıcı.
- `catalog/latest.json`: ECDSA P-256 ile imzalı test manifesti.
- `catalog/v3.json`: manifestte SHA-256 özeti bulunan test kataloğu.

**Güncelle**, yalnız kullanıcı düğmeye bastığında JSON indirir; katalog geçmişi ve kaynak performans kayıtları aynı tarayıcıdaki IndexedDB'de tutulur. Yayın için kullanılacak gerçek sağlayıcıların gömme ve kullanım izinleri ayrıca doğrulanmalıdır.

Bu LAB imza anahtarı üretimde kullanılmaz; özel imzalama anahtarları veya yönetici kimlik bilgileri bu public depoya yüklenmez.
