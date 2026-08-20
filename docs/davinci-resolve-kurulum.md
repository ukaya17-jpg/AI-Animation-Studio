# KURULUM — Neşeli Orman → DaVinci Resolve Otomatik Montaj

Bu kurulum **bir kere** yapılır, sonra script'i istediğin kadar bölüm için
kullanabilirsin.

## 1. DaVinci Resolve'da scripting'i aç

1. DaVinci Resolve'u aç.
2. Üst menüden **DaVinci Resolve > Preferences** (ya da **File > Preferences**).
3. **General** sekmesine git.
4. **"External scripting using"** ayarını **"Local"** yap.
5. Preferences'ı kapat, DaVinci Resolve'u **yeniden başlat**.

## 2. Ortam değişkenlerini ayarla (Windows)

Windows arama çubuğuna "ortam değişkenlerini düzenle" yaz, aç. **Kullanıcı
değişkenleri** altına şu 3 değişkeni ekle (Yeni... butonuyla):

| Değişken Adı | Değer |
|---|---|
| `RESOLVE_SCRIPT_API` | `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting` |
| `RESOLVE_SCRIPT_LIB` | `C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll` |
| `PYTHONPATH` | `%RESOLVE_SCRIPT_API%\Modules\` |

(Eğer `PYTHONPATH` zaten varsa, sonuna `;%RESOLVE_SCRIPT_API%\Modules\` ekle,
üzerine yazma.)

Ayarladıktan sonra **bilgisayarını yeniden başlat** (ortam değişkenlerinin
her yerde geçerli olması için en garantili yol budur).

## 3. Python paketlerini kontrol et

Terminalde (PowerShell):
```
python --version
```
3.6 veya üzeri olmalı (Blackmagic'in resmi desteklediği aralık 3.6-3.10
civarı ama genelde daha yeni sürümler de çalışır). Ekstra pip paketi
GEREKMİYOR — script sadece DaVinci'nin kendi modülünü kullanıyor.

## 4. Kurulumu doğrula

DaVinci Resolve'u aç, boş bir proje oluştur (ya da Resolve'un açılış
ekranında kalsın, script otomatik proje oluşturacak). Terminalde:

```
python -c "import DaVinciResolveScript as dvr; print(dvr.scriptapp('Resolve'))"
```

Eğer bir hata almazsan ve bir şey yazdırırsa (örn. bir obje referansı),
kurulum başarılı. `ModuleNotFoundError` alıyorsan 2. adımdaki ortam
değişkenlerini tekrar kontrol et ve bilgisayarı yeniden başlattığından
emin ol.

## 5. Script'i kullan

1. Platformdan bir bölümün "📦 Prodüksiyon Paketini İndir" ile ZIP'ini indir.
2. ZIP'i bir klasöre çıkart (ör. `Masaüstü/paylasma-bolumu/`).
3. DaVinci Resolve'un **açık** olduğundan emin ol.
4. Terminalde script'in olduğu klasöre git, çalıştır:
   ```
   python neseli_orman_montaj.py "C:/Users/SeninAdın/Desktop/paylasma-bolumu"
   ```
5. Script bitince DaVinci Resolve'da yeni bir proje ve timeline hazır
   olacak — Edit sekmesine geçip kontrol et.

## 6. (Opsiyonel) Fusion ile karaktere hareket ekleme

Script, karakter görsellerini timeline'a yerleştirir ama otomatik hareket
EKLEMEZ (bu, DaVinci sürümleri arası API farkları nedeniyle elle yapılması
daha güvenilir). Her karakter klibi için:

1. Timeline'da karakter klibine çift tıkla → Fusion sayfası açılır.
2. Sağ tık > Add Tool > Transform.
3. MediaIn1 çıkışını Transform girişine, Transform çıkışını MediaOut1'e bağla.
4. Timeline'ın başında Size'ı 1.0, ortasında 1.03, sonunda 1.0 yap (her
   noktada saat simgesine tıklayıp keyframe ekle) — bu hafif bir "nefes
   alma" hareketi verir.

## Sorun Giderme

| Sorun | Çözüm |
|---|---|
| `ModuleNotFoundError: No module named 'DaVinciResolveScript'` | Ortam değişkenlerini kontrol et, bilgisayarı yeniden başlat |
| "DaVinci Resolve'a bağlanılamadı" | DaVinci Resolve'un açık olduğundan ve Preferences'taki "External scripting" ayarının "Local" olduğundan emin ol |
| Ses/görsel dosyaları bulunamıyor | ZIP'in doğru çıkartıldığından, `assembly-manifest.json`'ın klasörün kökünde olduğundan emin ol |
| Altyazı otomatik eklenemedi uyarısı | Script yine de bir `.srt` dosyası oluşturur — DaVinci'de File > Import > Subtitle ile elle ekleyebilirsin |
