# TEST KULLANICI 026 — Gerçek canlı TV

Tarih: 26 Kasım 2026 (Türkiye)
Sürüm: 0.26 bağımsız kullanıcı testi
Kanal: Bir Gün TV, yayıncının yayımladığı HLS adresi
Sayfa: https://sedathut-sys.github.io/sefaxtv/live-tv-test/

## Kullanıcının aynen bildirdiği sonuç

> SefaXTV 0.26 gerçek TV kullanıcı testim:
> Görüntü: pass
> Ses: pass
> Not: çok iyi çalşıyor

## Kanıt
- Kullanıcı: görüntü PASS, ses PASS; olumlu oynatma deneyimi. Cihaz, tarayıcı, izleme süresi ve başlatma ayrıntıları ayrıca bildirilmedi.
- CI 45880365892 / 140117877162: 30.4654 s duvar zamanı, 30.466667 s medya ilerlemesi, 914 sunulan kare, 62 aralık, canlı HLS true, 512×288; 15 XHR HTTP 200. https://github.com/sedathut-sys/sefaxtv/actions/runs/45880365892
- Pages 45881764727: build ve deploy success, main 7d86f440181c46760018ed8f1e842bcada6412ce. https://github.com/sedathut-sys/sefaxtv/actions/runs/45881764727

## Kapsam ve karar
Bağımsız gerçek yayın test sayfasında kullanıcı PASS; ana akıllı izleyiciye gerçek HLS entegrasyonu henüz tamamlanmadı, açık kabul ayrıca bildirilmedi. Dublaj, alternatif ses, diğer kanallar, platformlar ve uzun süreli kararlılık test edilmedi. Kırmızı Bülten değildir. Ana izleyici, imzalı katalog ve önceki lab-test korunur. Sonraki adım: HLS adaptörünün ayrı akıllı izleyici entegrasyonu ve yerel, sıfır zorunlu servis maliyetli Türkçe dublaj prototipi.
