# SefaXTV 0.11 — Native LAB gözlemci protokolü

## Kapsam ve referanslar

SeFaSportsTV V1.10.23 Android ve V1.10.23.3 Windows dallarındaki `SeFaVideoObserver.java`, `MainActivity.java`, `MainForm.cs`, `observer.js` ve `bridge.js` salt okunur incelendi. Eski yayın alan adları veya izin listeleri kopyalanmadı. Eski sistemde ilk doğrulamada duran gözlemci yerine sürekli ilerleme kanıtı kullanılır. Astra mimarisinin izinli kaynak, tek iframe, manuel katalog güncellemesi ve belirsiz sonuç ayrımı korunur.

**Bu aşama yalnız izleyici köprüsü, kendi LAB oynatıcımız ve gözlemci referans kodudur.** Android APK ve Windows EXE/SDK kabukları bu sürümde üretilmedi. Gerçek üçüncü taraf iframe adaptörü yok. Kullanıcı tarafından imzalanan v4 katalog aynen korunur. `native-lab` merkezi katalog şemasına eklenmemiştir.

## Dosyalar ve güven sınırı

- Kök `index.html`: tek dosya web izleyicisi. Normal web tarayıcısında sadece mevcut kendi srcdoc LAB kaynağı kullanılır. Native LAB düğmesi saklıdır.
- `native/lab-player.html`: yalnız kendi ürettiğimiz canvas/video test içeriği. Native paketlemede tam olarak `/assets/lab-player.html` yoluna kopyalanacak.
- `native/observer.js`: yalnız `https://appassets.androidplatform.net/assets/lab-player.html` alt iframe'inde çalışan referans gözlemci. Harici alan adlarında çalışmaz. Native kabuk tarafından yalnız bu izinli yerel belgeye kurulması gerekir; APK/EXE hazır değildir.
- Ana belge native ortamda tam olarak `https://appassets.androidplatform.net/assets/index.html` olmalıdır. Ana belgeye özel Android `SefaXTVNative` veya Windows `chrome.webview` taşıyıcısı varsa iletişim açılır. Kamusal Pages sayfası native mesaj kabul etmez.

## Protokol (JSON string)

Bütün mesajlar `protocol: "sefaxtv-probe-v1"` taşır. Ana HTML yalnız kendi sabit paketlenmiş URL'sinde native taşıyıcıya erişir. Host tarafında mesaj kabulü ayrıca **ana frame kimliği ve tam URL** ile sınırlandırılmalıdır. Ana iframe tek başına yeni güvenilir köken kaydedemez.

1. `host:hello` → host gerçekten gözlemciyi kurabiliyorsa `host:ready`, `fixture: "https://appassets.androidplatform.net/assets/lab-player.html"` yanıtı. Native LAB ancak bu yanıttan sonra görünür.
2. Her denemede ayrı artan `seq` ve 128 bit rastgele `token`. `probe:start` mesajında bu değerler ve tam fixture URL'si vardır. URL fragmentinde `seq`, `token`, `mode` bulunur. Host yeni oturumu atomik açmalı; önceki oturumun frame kaydını geçersiz kılmalı. Yalnız tam eşleşen **canlı fixture frame kimliği** ve gerçek frame kökeni/URL ile bağlamalı; alt frame mesajında beyan edilen URL tek başına yeterli değildir. Yönlenme, yeniden yükleme, frame yok edilmesi, arka plan veya oturum değişiminde bağlam iptal edilir.
3. Observer her geçerli ilerlemede `video:advanced` mesajı yollar: `seq`, `token`, `url`, `counter` (artan), `method` (`frames`/`time`), `mediaTime`, `delta`, `frameDelta`. `frames` yönteminde en az 0,16 sn ilerleme ve artan kare; `time` yönteminde en az 0,25 sn ilerleme şarttır. Video duraklatılmış, bitmiş, seek halinde, görünmez, bağlı değil veya yeterli video boyutu yoksa kanıt verilmez. İki yöntem paralel, time denetimi 250 ms. Gönderimler en sık 700 ms. Host gerçek frame kimliği ve oturumu doğrulayıp, aktif/ön plandaysa bu mesajı ana belgeye iletir. Sıradaki iframe'in kanıtı önceki iframe'e bağlanamaz.
4. Ana HTML `seq`, `token`, tam URL, sayaç ve yöntem eşiğini yeniden denetler. `load` sadece hazır olma işaretidir; tek başına kapağı açmaz. 6,5 sn durum mesajı; 10 sn kanıt yoksa belirsiz deneme biter. Üç kaynaklık turda en fazla yaklaşık 30 sn ilk kanıt bekleme bütçesi, 8 sn oynatma ilerlemesiz durumda otomatik yedek. Görünmezken denetim bekler. Bilinmeyen sonuç kalite hatası değildir. Yeni kaynak önceki iframe'i kaldırır, `probe:stop` eski oturum bilgisiyle iletilir.

## Android / Windows kabuklarının bir sonraki entegrasyonu

Android: WebViewAssetLoader üzerinden yerel dosyaları ver; `WebViewCompat.addWebMessageListener` ve `addDocumentStartJavaScript` özellik desteğini önce denetle. Ana frame için `SefaXTVNative`, fixture alt frame için `SefaXTVProof` ayrı taşıyıcılar olmalı. Yerel kaynak kökeni dışına gözlemci kurulmaz. Mesajın gerçek `sourceOrigin` ve `isMainFrame` bilgisi, seçili fixture'ın doğrulanmış oturumuyla eşleşmeden iletilmez. Frame kimliğinin güvenilir biçimde bağlanamadığı cihazda native mod açılmaz.

Windows: WebView2 virtual host ile yerel assets; `CoreWebView2.WebMessageReceived` ana belge, `CoreWebView2Frame.WebMessageReceived` aktif ve doğrulanmış fixture frame için ayrı denetimler. Frame lifecycle/navigation olayları ile oturumu iptal et. `Form.Deactivate` yalnız başka pencereye tıklanınca yayını durdurmamalı; minimize/restore ayrı ve taze kanıt gerektirir. `host:ready` gerçek kabuk hazır olmadan gönderilmemeli.

Her iki ortamda üçüncü taraf kaynaklara yönelik çalışma ayrıca resmî gömme ve gözlem izni, sabit HTTPS kökeni, gerçek frame kimliği ve sağlayıcıya özgü kabul testi gerektirir. CSP, X-Frame-Options, DRM veya erişim korumalarına müdahale edilmez. Kaynak içindeki reklam/maç/hak durumu video ilerlemesiyle doğrulanmış olmaz.

## 0.11 testleri

- Gerçek Chromium LAB video: açılışta iframe yok, oynatma kanıtı, eski oturum/yanlış köken reddi, hata ve donma yedeği geçti.
- Native taşıyıcı **taklit edilen** Chromium testinde yanlış seq, token, URL, eşik, mesaj tipi ve kare farkı reddi; geçerli iki kanıt türü, tekrar mesajı ve kanal değişiminde stop doğrulandı.
- Gözlemci Node VM testi: iki kanıt türü, artan heartbeat, duraklama/seek, yanlış köken ve ana frame reddi. Bu test fiziksel WebView/WebView2 çalıştırmaz.
- Kullanıcının imzalı v4 paketinin ECDSA imzası, SHA-256 ve pinlenmiş açık anahtarı doğrulandı. Gerçek GitHub Pages tarayıcı erişimi bu ortamda engelli; fiziksel native ve canlı IndexedDB testleri açık kalıyor.
