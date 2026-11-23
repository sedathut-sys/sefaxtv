# SefaXTV 0.10 — 7/24 spor iframe araştırması ve kabul kapıları

**24 Kasım 2026 — Araştırma kaydı. Yayın/kullanım izni kaydı değildir.**

## Hedef

5–20 spor kanalı; kanal başına en fazla 20 alternatif. Her kanal seçildiğinde kaynaklar yerel güvenilirlik sıralamasına göre **birer birer**, mevcut oynatıcının üstünde koruyucu kapakla denenir. Tek seferde bir iframe çalışır; hiçbir genel site taraması arka planda başlatılmaz. İki gerçek kare ve ilerleyen medya zamanı kanıtı gelince kapak kalkar. Devam eden kare ilerlemesi 8 saniye boyunca kesilirse kapak geri gelir ve sıralı yedeğe geçilir; belirsiz durma kesin başarısızlık sayılmaz. İlk tur en çok üç aday; varsa kalan adaylar için izleyici onayı gerekir. Yerel skor ve beklemeler IndexedDB'de saklanır.

## Benzer yayın sitesi araştırması

| Ad / gözlem | 7/24 kanal listesi | Resmî yeniden gömme hakkı | Doğrulanmış kare/oynatma olay API'si | Kamu kataloğuna kabul |
|---|---|---|---|---|
| ArdaSportV / Arda Spor TV (kullanıcının belirttiği ad) | Site kimliği bu araştırmada kesin doğrulanamadı | Belge yok | Belge yok | **Hayır** |
| Bahiks22 TV, `bahikstv22.com` | beIN Sports, S Sport, Tivibu Spor, TRT Spor vb. listeleniyor | Belge bulunmadı | Belgeli oynatma köprüsü bulunmadı | **Hayır** |
| Netspor, `netspor.co` | 7/24 ve maç listesi bulunuyor | Belge bulunmadı | Belgeli oynatma köprüsü bulunmadı | **Hayır** |
| Webspor, `webspor.co` | 7/24 ve spor kanal listesi bulunuyor | Belge bulunmadı | Belgeli oynatma köprüsü bulunmadı | **Hayır** |
| Pusula Yayın, `pusulayayin.vip` | 7/24 çok sayıda spor kanalı listesi bulunuyor | Belge bulunmadı | Belgeli oynatma köprüsü bulunmadı | **Hayır** |
| Zbahis TV ve Marsbahis TV | 7/24 ücretli spor kanalı isimleri listeleniyor | Belge bulunmadı | Belgeli oynatma köprüsü bulunmadı | **Hayır** |

**Uyarı:** Bir listede kanal isminin görünmesi veya iframe URL'si bulunması, yeniden gösterim / iframe için yayın haklarının alındığı anlamına gelmez. Bu platformlardaki potansiyel ücretli yayın akışı URL'leri, tokenlar, manifestler veya koruma atlama yöntemleri araştırma kaydına ve SefaXTV kataloğuna alınmamıştır. Web aramasında içerik adı bulunmasıyla 7/24 video oynatmanın doğrulandığı da ileri sürülmüyor.

## İzinli sağlayıcı kabul listesi

1. Yayıncı veya yetkili dağıtımcıdan **kanala/ülkeye/cihaza/iframe kullanıma özel** yazılı izin ya da açık platform şartı.
2. Yalnızca sağlayıcı tarafından belgelenmiş **HTTPS iframe player-only** URL şablonu. Kamu kataloğu serbest URL taşıyamaz; `provider` + `contentId` taşır. Alan adı ve yol listesi **uygulama kodunda** pinlenir.
3. Gömme CSP `frame-ancestors`, `X-Frame-Options`, DRM, bölge, ödeme ve resmî oynatıcı görünümü kurallarına uyum. Engel atlatma, proxy, iç DOM okuma, reklam/branding kırpma yoktur.
4. Belgelendirilmiş oynatma kanıtı (iki video karesi veya kabul edilmiş oynatma+ilerleme olayı), tam köken ve kaynak penceresi kontrolü, tekil oturum/kanal kimliği. `iframe.onload`, HTTP 200, buffer/ready tek başına başarı değil.
5. En az iki gerçek tarayıcı ve iki kökende kabul testinden sonra **yeni derlemeye adaptör ekleme**. Adaptör eklenmeden imzalı katalog içine bilinmeyen sağlayıcı sokulamaz.
6. İzin kaldırılmışsa katalogdan kaynak çıkarılır ve sonraki güncellemeyle cihazlara revokasyon ulaşır.

## 0.10 uygulama durumu

- `index.html` tek HTML; `CLIENT_BUILD=10`. Mevcut imzalı **v4** 6 LAB kanalı / 25 LAB kaynağı korunur. Altıncı kanal `imzali-v4` testidir.
- Sadece `lab-internal` izni için `srcdoc` adaptörü etkin. Üçüncü taraf alan adları / kaynak URL'leri **etkin değil**.
- Oturum kimliği, `event.source` ve LAB kaynak türü denetlenir. `event.origin='null'` yalnız sandboxed `srcdoc` için kabul edilir. Yeni resmî üçüncü taraf adaptöründe **tam güvenilir HTTPS origin** zorunlu olacaktır.
- Başarı kanıtı: frame callback'le iki ilerleyen medya zamanı / kare; devamında ~1 sn ilerleme bildirimleri; 8 sn durmada yedek. 6,5 sn kanıtsız timeout **unknown**. Açık hata yalnız `lab-fixed-error` olunca **failure**. Aynı anda tek iframe.
- Test bilgisi → **Donma → yedek testi**, imzalı katalogu değiştirmeden geçici kendi LAB videosuyla donma ve yedeği gösterir.
- Geçmiş veritabanı `akilli-web-tv-lab-v03` sürüm 3 korunur. Güncelle ancak izleyici düğmeye bastığında yapılır.

## Kaynaklar

- Bahiks22 liste: https://bahikstv22.com/
- Netspor liste: https://netspor.co/
- Webspor liste: https://webspor.co/
- Pusula liste: https://pusulayayin.vip/izle/
- Zbahis örnek liste: https://zbahistv67.com/
- Marsbahis örnek liste: https://www.marsbahistv400.com/
- MDN iframe yükleme semantiği: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe
- MDN postMessage köken doğrulama: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
- Astra mimari raporu: projeye kullanıcı tarafından sağlanan özel doküman (repo içinde yayımlanmadı)