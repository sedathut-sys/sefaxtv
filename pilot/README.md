# SefaXTV 0.15 — İlk gerçek iframe pilotunun ön kabulü

## Sonuç — 25 Kasım 2026
0.14 GitHub Actions 45689497521 başarılı. Altı senaryo: load/ready kapak açmaz; gerçek kareler iki ayrı loopback kökeninde doğrulanır; yanlış origin/window/seq reddedilir; kesin hata yedeği; donma yedeği; izin verilmeyen parent CSP tarafından engellenir. Bu, gerçek dış sağlayıcı veya fiziksel native kabulü değildir.

Astra raporundaki resmî player-only iframe, kapak izni, platforma özgü kanıt, Türkiye kapsamı, kullanıcı tarafından başlatılan oynatma, imzalı manuel katalog ve ücretsiz izin koşulları korunuyor. Native gözlemci sadece mevcut kendi LAB içeriğinde etkin. Üçüncü taraf DOM'una erişim için güvenlik mekanizması aşılmaz. IPTV/akış adresi, gizli token, proxy veya üçüncü taraf oynatıcı enjeksiyonu araştırılmadı.

## Adaylar
Kaynaklar ve kararlar candidates.json içindedir; bu araştırma kaydı katalog değildir.
- İlk spor pilotu adayı: **WSBN TV Channel 1 (24/7)**. https://www.wsbn.tv/wsbn-tv-station/ ve https://www.wsbn.tv/wsbn-tv-schedule/ sürekli program ve canlı etkinlikleri tanıtıyor. Gömme teklifi takım/lig/dernek yayın ortaklarına yöneliktir. SefaXTV adına ücretsiz izin, tam iframe URL'si, geçici marka kapağı, ilerleme bildirimi ve native gözlem izni henüz doğrulanmadı. Yayıncıdan teyit gerekir. https://www.wsbn.tv/terms/ .
- Chess.com: https://www.chess.com/article/view/how-to-embed-share-chess-media resmî Twitch yayınlarını gömmeye ilişkin bilgi veriyor. https://dev.twitch.tv/docs/embed/ oynatıcının örtülmemesi şartını koyuyor. Mevcut markalı kapakla uyumsuz; etkin değil.
- A Spor ve TRT Spor: resmî yayın/şart sayfaları var; gerekli gömme, kapak ve kanıt hakları doğrulanmadı.
- UEFA.tv: planlı spor etkinlikleri, 7/24 lineer yayın olarak kabul edilmez. Kullanım koşulları da ayrıca kısıtlayıcı.
- UN Web TV: https://www.un.org/en/node/205121 etkinliklerin gömme kodlarını paylaşmaya açıkça izin verildiğini bildiriyor. Spor değil, 7/24 süreklilik, belirli oynatıcı URL'si, kapak ve kanıt izni teyit edilmedi.

## Kod ve test
eligibility.mjs: çevrimdışı, insan incelemesinden sonra kullanılan ön kontrol; kendi başına lisansı doğrulamaz, katalog üretmez, ağ isteği yapmaz, hiçbir iframe açmaz. Adayların tamamında approval=null. İlk pilot için yalnız sabit ve kesin HTTPS origin/path biçimi kabul edilir; sorgu parametreli resmî embed söz konusu olursa ayrı kod incelemesi gerekir. Kabul belgeleri, tarih, Türkiye, maliyet, kapsam, kapak, zorunlu bileşenler, web/native kanıt ve cihaz kabulü ayrı tutulur. Üretim öncesinde ayrıca Türkiye'deki dağıtım modelinin hukuki kapsamı netleşmelidir.

Test: `node pilot/test-eligibility.mjs`. Aynı fonksiyon ve testler JavaScript ortamında 47/47 başarılı; gerçek adayların tümü üç platformda bloke, yalnız sentetik test kaydı geçer. Bu testler gerçek yayın oynatmaz. Node dosyası ayrı CI çalıştırılmadı.

## Sonraki şart
publisher-request.md gönderilmemiş izin talebi taslağıdır. İlk gerçek pilot WSBN Channel 1 ile sınırlıdır. Yayıncı onayı geldikten sonra tam iframe URL'si, normal tarayıcı politikaları, kanıt ve geçici kapak şartı incelenir. Her platform ayrı gerçek kabul testini geçmeden açılmaz. Kamu kataloğunda onaylı harici kaynak sayısı sıfır. main, v4 katalog ve manifest değiştirilmedi. Fiziksel Android/Windows kabulü açık.
