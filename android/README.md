# SefaXTV 0.12 — Android LAB (ayrı test dalı)

Bu Android kaynak projesi, web 0.11 izleyicisinin tek HTML yapısını koruyup Android için 0.12 köprüsünü ekler. Eski DunyaTV Android V1.10.23 kodu yalnız referans olarak okundu. Capacitor yerine doğrudan AndroidX WebView seçildi: eski uygulamanın native mesajlaşma mimarisiyle uyumluluk ve daha az bağımlılık. Astra raporundaki yerel paketleme, imzalı manuel katalog, platforma özel test ve izin şartları korunur. Android telefon LAB hedefidir; TV/Box, Windows ve üçüncü taraf sağlayıcılar henüz etkin değildir.

- Yerel ana HTML ve kendi canvas/video fixture'ı WebViewAssetLoader üzerinden açılır. `addWebMessageListener` yalnız kesin yerel HTTPS origin'inde çalışır; host sadece ana frame mesajını kabul eder. Document-start gözlemcisi yalnız tam yerel fixture URL'sinde çalışır.
- AndroidX mesaj dinleyicisi doğrudan alt frame'in kimliğini vermez. Bu yüzden kendi fixture gözlemcisi `postMessage` ile paketlenmiş ana belgeye kanıt iletir; ana belge gerçek `event.source === active.frame.contentWindow`, tam origin, canlı aynı-kökenli iframe URL, seq/token denetler, host ise tekrar oturum/sayaç/zaman/kare eşiklerini doğrular. Bu yaklaşım sadece kendi güvenilir yerel iki belge için geçerlidir. Üçüncü taraflara taşınmaz.
- Uygulama ağ erişimi yalnız GitHub Pages'in sabit katalog JSON yollarına açık. CORS ve HTTPS normal tarayıcı kurallarıyla uygulanır; erişim veya DRM aşılmaz. `file:`/`content:`/mixed content ve dış gezinme kapalı. Üçüncü taraf cookie yok. Katalog imza anahtarı APK imzasından ayrıdır. Kullanıcının v4 manifesti ve katalogu değişmedi.
- `onPause` eski oturumu iptal eder, iframe'i kaldırır, boş belgeye gider ve WebView duraklatılır. Dönüşte yerel ana belge yeni oturumla açılır; kullanıcı yeniden seçer. Yerel IndexedDB depolaması temizlenmez. Gerçek cihazda ses kesme ve kalıcılık test edilmeli.
- Özellik desteği yoksa native düğmesi açılmaz; web LAB kullanılabilir. İlk açılışta yayın başlamaz. Native LAB: donan kaynak ardından çalışan yedek.

## Derleme

JDK 17, Gradle 8.11.1, Android SDK 35, Android Gradle Plugin 8.9.2, AndroidX WebKit 1.14.0. Proje dizininde `gradle :app:assembleDebug`. Debug APK `app/build/outputs/apk/debug/app-debug.apk`. Yerel `gradle`/SDK veya GitHub Actions gereklidir. Özel anahtar veya parola gerektirmez. Debug APK mağaza dağıtımı için değildir.

## Test

`javac -d /tmp/sefa-gate app/src/main/java/com/sefaxtv/lab/ProbeGate.java tests/ProbeGateTest.java && java -cp /tmp/sefa-gate com.sefaxtv.lab.ProbeGateTest`.

Fiziksel Android kabulü: ilk açılışta iframe olmaması; Güncelle v4 ve 6 kanal; uygulama kapanıp açıldığında katalog/favori; Native LAB ile kanıt/donma/yedek; kanal değiştirince eski mesajın reddi; arka plana alındığında ses ve görüntü durması; dönüşte yeni kullanıcı seçimi. Bu testler gerçek cihaz olmadan geçti sayılmaz.
