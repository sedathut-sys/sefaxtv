# SefaXTV 0.16 — Spor araştırması ve harici VOD tanı testi

25 Kasım 2026. 0.15'in altı adayı korunur. sports-research.json yedi yeni inceleme kaydı içerir. CBS Golazo, Red Bull TV, SPORT+ ve ACI Sport TV gerçek lineer spor yayıncısı adaylarıdır; halka açık izleme, gömme ve geçici kapak haklarının yerine geçmez. ScoreBat bir video widget'ı, SPORT.VIDEO kendi içeriğini gömme platformu, NASA Live ise genel TV araştırma adayıdır. Bu kayıtlar katalog değildir. Onaylı 7/24 spor kaynağı: 0. IPTV/M3U8, rastgele aracı iframe, koruma aşma ve kaynak çıkarma yok.

## Harici teknik pilot (spor/canlı değil)
Blender Foundation'ın kendi PeerTube örneğinde Big Buck Bunny:
- Hak sahibinin lisansı: https://peach.blender.org/about/ ; Creative Commons teyidi: https://creativecommons.org/2008/06/13/big-buck-bunny-beautiful-cc-licensed-3d-short/ ; CC BY 3.0: https://creativecommons.org/licenses/by/3.0/ .
- Resmî video: https://video.blender.org/w/pAQiVCgv2CsLg79KKXUoMw ; Blender'ın kendi site kodunda içerik kimliği: https://projects.blender.org/infrastructure/blender-org/commit/8f83d84e288288d0bf21c8cae5ae5c6f9f0f7217 .
- Belgeli iframe/oynatıcı mesajlaşması: https://docs.joinpeertube.org/api/embed-player . Yerel testte npm @peertube/embed-api@0.2.0 (AGPL-3.0; lisans/kaynak referansı https://www.npmjs.com/package/@peertube/embed-api) kullanılır. SDK dosyası depoya eklenmez, CI'da geçici olarak yüklenir. Bu bir kanal arama API'si değildir.
- Tanı testi sağlayıcının iframe'ini kullanıcı düğmesine basınca açar, P2P kapalı, ses başlangıçta kapalı, kontrol ve marka öğeleri korunur. Oynatıcı örtülmez, içerik kopyalanmaz/değiştirilmez. Atıf ve lisans bağlantıları ekrandadır.
- Belgelenmiş playbackStatusUpdate olayında playing ve artan iki zaman aralığı istenir. SDK hazır/load başarı değil. Bu sağlayıcının bildirdiği VOD zaman kanıtıdır; native gerçek kare gözlemcisi, maç kimliği, canlılık veya üretim güvenlik kabulü değildir. SDK'nın kaynak pencere/köken kontrolü ve atıf/kapak şartları üretimden önce ayrıca incelenir. Oturum değişince eski callback geçersiz ve iframe kaldırılır. 20 sn başlangıç, 8 sn donma belirsiz kabul edilir.
- Bu bağımsız, örtüsüz tanı aracı Astra'nın katı TV kapağına istisna olarak canlı uygulamaya dahil edilmez. Main, Android/Windows dalları ve imzalı v4 kataloğu değiştirilmez. Native gözlemci üçüncü tarafa kurulmaz. Gerçek oynatma doğrulanmadan başarılı denmez; GitHub loopback kabulü Türkiye/HTTPS dağıtım veya fiziksel cihaz kabulü değildir.

## Test
node pilot016/test-progress.mjs (14 kontrol). 
npm install --no-save --ignore-scripts --package-lock=false @peertube/embed-api@0.2.0
mkdir -p pilot016/vendor
cp node_modules/@peertube/embed-api/build/player.min.js pilot016/vendor/
python -m pip install playwright==1.52.0
python -m playwright install chromium
python pilot016/test_external.py
Dış ağ/sağlayıcı engeli veya zaman kanıtı yoksa test 2 çıkış kodu ile UNKNOWN verir. Bir sonraki gerçek spor pilotu ancak yayıncı onayı ve tam şartlar tamamlanınca yapılabilir.
