# SefaXTV — Akıllı Web TV

**İzleyici: 0.9**, yalnız kendi ürettiğimiz laboratuvar görüntüsü. Site herkese açıktır:
https://sedathut-sys.github.io/sefaxtv/

## Mevcut yayın

- `index.html`: tek HTML izleyici, CLIENT_BUILD=9; imzalı katalog okuma, favori, arama, kategori, örtülü oynatma.
- `catalog/latest.json`: **hâlâ sağlam v3 manifesti**; bu anahtara dokunulmadı.
- `catalog/v3.json`: **hâlâ sağlam v3 katalog**; bu dosyaya dokunulmadı.
- GitHub Pages yalnız kullanıcının Güncelle düğmesine basmasıyla katalog okunacak HTTPS adrestir. İçerikte yalnız laboratuvar kaynakları vardır.

## 0.9 imza anahtarı geçişi — henüz tamamlanmadı

Özel anahtar **yalnız yönetici bilgisayarında** oluşturulacak. Yerel yönetici imzalama HTML'i, şifreli yedek, parolalar, taslak dosyalar, GitHub tokenları ve izin belgeleri **public depoya konulmaz**.

Yönetici kendi bilgisayarında yerel HTML ile yeni P-256 anahtarı üretir, PBKDF2-SHA256 / AES-256-GCM şifreli yedeğini ve parolasını güvenle saklar, yedeği tekrar açmayı test eder. Yerel araç mevcut 5 test kanalını ve kaynak kimliklerini koruyan, ayrıca bir imzalı test kanalı ekleyen v4 taslağını imzalar. Dışa aktarılan **tek kamusal teslim paketinde** sadece `keyId`, `publicJwk`, `catalogText` ve `latestText` gibi kamuya açık bilgiler bulunur.

Paket geldiğinde yayın işlemi **her adım doğrulandıktan sonra** yapılır:

1. Kamusal paket anahtar kimliği, imza, katalog SHA-256 ve v4 şeması doğrulanır.
2. `publicJwk` güvenilen açık anahtar listesine eklenir; GitHub Pages dağıtımı başarılı olana kadar katalog değişmez.
3. Önce `catalog/v4.json` yayımlanır; bu dağıtım ve yayımlanacak baytların özeti doğrulanır.
4. **En son** `catalog/latest.json` işaretçisi v4'e değiştirilir; daha eski sürümle geri alma yapılmaz.

Ayrı yöneticinin özel imza anahtarı olmadan veya işbu kontroller geçmeden **v4 kamuya yayımlanmaz**. Bu, bilinmeyen bir açık anahtarı otomatik olarak kabul eden güvensiz bir düzenek değildir.

GitHub Pages herkese açık statik bir sitedir; bu depo özel erişim sağlamaz. İzinli üçüncü taraf sağlayıcı adaptörü ve gerçek kanal hâlâ yoktur.
