# SefaXTV 0.13 — Windows LAB

Ayrı Windows test dalı. Canlı web 0.11, Android 0.12 ve imzalı v4 katalog değiştirilmez. SeFaSportsTV 1.10.23.3 Windows kaynakları ve Astra raporu salt okunur referanstır; eski sağlayıcı adresleri aktarılmaz. Bu dal yalnız kendi LAB içeriğini oynatır.

- .NET 8 WinForms, WebView2 1.0.4314.35 (önceki Windows referansındaki sürüm). Ana HTML ve iki yerel kaynak EXE içine gömülür. Native uygulama ayrı WebView2 profilinde IndexedDB kullanır. Güncelle yalnız sabit HTTPS katalog adresine normal CORS üzerinden istek yapar; imza doğrulaması değiştirilmedi. Yeni kurulum başlangıç kataloğundan başlar; Güncelle ile v4 alınır.
- Ana frame tam yerel URL; doğrudan fixture iframe için host tarafından doğrulanan navigasyon URL'si ve canlı frame nesnesi. `probe:start` ardından `probe:armed` gelmeden iframe DOM'a eklenmez. Eski token/seq, yanlış frame, URL, tekrar sayaç, zaman gerilemesi ve zayıf kanıt reddedilir. Frame yeniden navigasyon/yok edilme, stop veya minimize durumunda bağlam iptal edilir. Focus kaybında yayın durdurulmaz; restore sonrasında kullanıcı yeniden kanal seçer.
- Yerel observer yalnız tam fixture URL'sinde çalışır. 0.16 sn kare veya 0.25 sn zaman ilerlemesi; sürekli heartbeat. Donmada 8 sn sonra yedek; 20 kaynak üst sınırı, üç aday/tur ve yerel sıralama korunur. Dış iframe, DRM/CSP aşma, kaynak URL çıkarma veya proxy yok.
- Windows x64 GitHub CI: C# gate testleri ve self-contained debug amaçlı yayın; Windows'ta WebView2 Runtime gerekir. Gerçek WebView2/cihaz oynatma, minimize/restore ve gerçek HTTPS/IndexedDB kabul testleri ayrı doğrulanmalıdır; derleme tek başına oynatma kanıtı değildir.

Yerel derleme: `dotnet run --project tests/GateTests.csproj`, `dotnet publish SefaXTV.WindowsLab.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o publish`.
