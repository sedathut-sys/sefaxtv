# SefaXTV 0.17 — Harici VOD tanı LAB (26 Kasım 2026)

Başlangıç: 0.16 commit bfc83b414846ed211145609647454c02f96534cc. 0.16 Actions 45691706723: 14 kontrol ve seçim öncesi iframe yok PASS; harici VOD 20 saniye içinde kanıt yok UNKNOWN, çıkış 2. Sebep henüz kanıtlanmadı.

0.17 bağımsız tanı: aynı açık lisanslı Blender Foundation videosu, aynı SDK sürümü; ayrı temiz tarayıcı oturumlarında muted autoplay ve kullanıcı düğmesiyle belgeli API play deneyi. Manuel API düğmesi, oynatıcının içindeki gerçek kullanıcı Play hareketiyle eşdeğer değildir; fiziksel tarayıcı testi ayrıca gereklidir. API ready, load, status değişimleri, konum ve gate ret gerekçesi kayda alınır. Ağ özeti yalnız köken, kaynak türü ve HTTP durum/istek hatası; URL sorgusu, gövde, token yok. İlk hazır olma ve ilerleme süreleri ayrıldı (20+20 sn); iki artan geçerli zaman aralığı korunur. Sürekli kanıt 8 sn sonra sona erer. İlk kanıt alınmadıkça PASS yok. İki moddan biri UNKNOWN ise CI çıkış 2. Bu yalnız sağlayıcı VOD zaman beyanı, gerçek video karesi/ canlı spor veya fiziksel cihaz kabulü değildir.

Belgeler: https://docs.joinpeertube.org/api/embed-player . Oynatıcı örtülmez, kontrol ve marka korunur, P2P kapalı. SDK bağımlılığı CI'da geçici, depoya eklenmez. Üçüncü taraf DOM'una erişilmez, koruma aşılmaz. Ana dal, eski LAB dalları, imzalı katalog, gerçek spor adayları değişmez. Kırmızı Bülten değildir.

Yerel: node pilot017/test-progress.mjs; npm install --no-save --ignore-scripts --package-lock=false @peertube/embed-api@0.2.0; mkdir -p pilot017/vendor; cp node_modules/@peertube/embed-api/build/player.min.js pilot017/vendor/; python -m pip install playwright==1.52.0; python -m playwright install chromium; python pilot017/test_external.py. Fiziksel tarayıcı için pilot017 klasörünü yerel HTTP sunucusunda açın; iki modun durumlarını ve gerçek görüntüyü gözlemleyin.

Sonuç: CI ve fiziksel kabul henüz doğrulanmadı; test çalışması sonunda ham kayıtlar incelenir.
