# SefaXTV 0.14 — Kabul ve izinli iframe pilotu

## Durum (25 Kasım 2026)
Android 0.12: Actions 45685857799, commit 884ff5d0ae81edbfd85172656e8b23138ddbe32e, başarılı debug APK, artifact 15056856407, 26 Java testi.
Windows 0.13: Actions 45687442653, commit 295c31f76810c4c453d836d3fcc0f9acd5f4925f, başarılı x64 yayın, artifact 15056628162, 39 C# testi.
Yerel tekrar: Android Java 26, iki gözlemcinin Node VM denetimleri, Chromium gerçek canvas/video, hata/donma yedeği, yanlış köken/oturum, Android taklit host relay, Windows taklit host armed/heartbeat/suspend ve v4 ECDSA/hash kontrolü geçti. Bunlar gerçek cihaz sonucu değildir. Bu ortamda SDK/emülatör ve WebView2 yok; iki ayrı ağ kökenine Chromium erişimi yönetici politikasıyla engellendi.

## Yerel test düzeneği
test_two_origins.py yalnız kendi ürettiğimiz canvas videosuyla izole loopback kökenleri kullanır. Başka köken içindeki DOM okunamaz; gerçek video karelerinden sağlayıcı işbirliğiyle mesaj gelir. Doğru origin, gerçek event.source, oturum, artan sayaç ve kare/zaman denetlenir; hazır/yükleme tek başına başarı değildir. Kaynak hata/donma yedeği ve izin verilmeyen parent için CSP frame-ancestors denetlenir. Bu, gerçek uygulamaya henüz bağlanmamış ayrı kabul düzeneğidir; üçüncü taraf API araması, iframe linki çıkarma, DRM/CSP müdahalesi veya proxy yok. CI sonucuna bakmadan geçildi sayılmaz.

## Fiziksel kabul matrisi (henüz açık)
| Test | Android | Windows |
|---|---|---|
| Temiz kurulum: iframe yok, manuel seçim | Bekliyor | Bekliyor |
| Native LAB: örtülü video gerçek ilerleme; ilk kanıt sonrası kapak açılır | Bekliyor | Bekliyor |
| Donma: kapak geri gelir; tek yedek oynar | Bekliyor | Bekliyor |
| 20 hızlı kanal geçişi, tek iframe/ses, eski kanıt yok | Bekliyor | Bekliyor |
| Arka plan/minimize, ses durur, dönüşte taze seçim/kanıt | Bekliyor | Bekliyor |
| Başka pencereye tıklamak yayını kesmez | Uygulanmaz | Bekliyor |
| Güncelle öncesi sıfır katalog isteği; v4 ile 6 kanal; favori ve IndexedDB kalıcılığı | Bekliyor | Bekliyor |
| Çevrimdışı açılış; yanlış imza ve eski sürüm reddi | Bekliyor | Bekliyor |

## Gerçek izinli iframe kabul kartı
Her aday için aşağıdaki bilgiler yönetici tarafından doğrulanır. Bir adayın açık internetten erişilebilir olması veya video ilerlemesi, gömme hakkını/maçın kimliğini ispatlamaz.
- Yetkili yayıncı, kanal kimliği, izin belgesi/açık şartların referansı, geçerlilik süresi, ülke ve platform kapsamı; uygulama kökeni için iframe hakkı; native gözlem için ayrıca açık izin.
- Sağlayıcının resmî player-only HTTPS adres şablonu ve sabit kökeni. Gömme CSP/X-Frame-Options, DRM, bölge, kullanıcı hareketi, reklam/marka gösterimi şartları korunur. Video dışı zorunlu bileşen gizlenmez.
- Web: sağlayıcı işbirliğiyle güvenilir oynatma/ilerleme bildirimi (harici API hizmeti zorunlu değil); yoksa bilinmeyen ve kapak kapalı.
- Native: yalnız izinli ortam ve belgeli kaynak; gözlemci aktif frame/URL ve oturumla güvenilir eşleştirilebilir olmalı. Android yerel relay yaklaşımı üçüncü taraflarda kullanılamaz; ayrı güvenlik incelemesi gerekir. Windows'ta gerçek frame lifecycle ve kaynak kökeni ayrıca kontrol edilir.
- Her platformda bağımsız fiziksel kabul, gerçek izinli yayının doğru içerik olduğunun doğrulanması, kapak ve donma/yedek kontrolü; gerekirse autoplay için kullanıcı hareketi. Başarılı olmayan platformda aktif etme.
- Yeni adaptör ancak kod incelemesi sonrası; imzalı katalogda serbest HTML/JS veya rastgele URL yok, kanal başına en fazla 20 kaynak, yalnız kullanıcı Güncelle ile yeni imzalı sürüm etkinleşir. İzin iptalinde kaynak çıkarılır, daha yüksek sürümle imzalanır.

Şu an doğrulanmış harici aday sayısı: **0**. v4 katalog ve main dalı değişmedi. İlk pilot bir gerçek izinli yayıncıyla sınırlıdır. Bu dal test ve kabul referansıdır; APK/EXE sürümü değişmedi.
