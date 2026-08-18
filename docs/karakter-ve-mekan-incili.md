# Karakter ve Mekan İncili

Bu dosya, Neşeli Orman'ın sabit içerik bankasındaki (`backend/app/services/content_bank.py`)
tüm karakterlerin, mekanların ve temaların insan-okunur bir referansı. Kod
zaten tek doğruluk kaynağı (single source of truth) — bu dosya onu tekrar
üretmez, sadece bir bölüm yazarken/tanıtırken hızlıca bakılabilecek bir
özet sunar. **İlk kez bu turda oluşturuldu** (3 yeni karakter + 2 yeni mekan +
8 yeni tema eklenirken); önceki 5 karakter/4 mekan/20 tema için ayrı bir
"incil" dosyası daha önce yazılmamıştı, bu yüzden aşağıdaki tablolar hem
eski hem yeni içeriği birlikte kapsıyor.

Ses eşlemeleri için ayrıca bkz. [docs/ses-rehberi.md](ses-rehberi.md).

## Karakterler (8)

| id | İsim | Tür | Rol | Temel Değer | Kişilik | Catchphrase |
| --- | --- | --- | --- | --- | --- | --- |
| `zeytin` | Zeytin | Baykuş | Bilge Öğretmen | Merak ve Öğrenme | sakin, meraklı, sabırlı, bilgili | "Hadi birlikte keşfedelim!" |
| `findik` | Fındık | Sincap | Enerjik Şakacı | Paylaşma | hareketli, cömert, komik, sabırsız ama sevecen | "Paylaşınca daha lezzetli oluyor!" |
| `minik` | Minik | Tavşan | Çekingen Kalp | Cesaret ve Arkadaşlık | utangaç, nazik, duyarlı, gelişen özgüven | "Sanırım... deneyebilirim!" |
| `boncuk` | Boncuk | Ayı Yavrusu | Koruyucu Büyük Kardeş | Yardımlaşma ve Aile | güçlü, koruyucu, sakin, güvenilir | "Birlikte taşırsak, yük hafifler." |
| `papatya` | Papatya | Arı | Çalışkan Takım Oyuncusu | Takım Çalışması ve Sayılar/Bilim | çalışkan, düzenli, meraklı, pozitif | "Bir, iki, üç... birlikte daha güçlüyüz!" |
| `kurnaz` | **Kurnaz** *(yeni)* | Tilki | Zeki Problem Çözücü | Yaratıcı Düşünme | zeki, kurnaz ama iyi kalpli, kendinden emin, meraklı | "Bir problem mi var? Hemen bir çözüm bulabilirim!" |
| `diken` | **Diken** *(yeni)* | Kirpi | Çekingen ama Sevimli | Kendini Kabul Etme | utangaç, duyarlı, içten, kendini geliştiren | "Ben... çok da farklı değilim aslında." |
| `isik` | **Işık** *(yeni)* | Ateşböceği | Umut Veren Rehber | Umut | umutlu, sakin, yol gösterici, nazik | "Karanlık bazen korkutucu görünür ama merak etme, ben yolunu aydınlatırım." |

### Görsel betimlemeler ve varlıklar

| id | Görsel betimleme | Görsel | Ses örneği |
| --- | --- | --- | --- |
| `zeytin` | Kahverengi-turuncu tüylü, büyük yuvarlak gözlüklü genç bir baykuş; boynunda küçük bir kitap dolu çanta. | `/static/characters/zeytin.png` | `/static/characters/voices/zeytin.mp3` |
| `findik` | Kızıl-kahve tüylü, büyük kabarık kuyruklu küçük bir sincap; sırtında fındık topladığı minik bir çanta. | `/static/characters/findik.png` | `/static/characters/voices/findik.mp3` |
| `minik` | Yumuşak beyaz tüylü, uzun kulaklı küçük bir tavşan; kulaklarından biri hafif eğik, boynunda mavi fular. | `/static/characters/minik.png` | `/static/characters/voices/minik.mp3` |
| `boncuk` | İri yapılı ama sevimli, koyu kahverengi tüylü bir ayı yavrusu; patisinde ailesinden kalma küçük bir yonga. | `/static/characters/boncuk.png` | `/static/characters/voices/boncuk.mp3` |
| `papatya` | Sarı-siyah çizgili, parlak saydam kanatlı küçük bir arı; küçük bir defter ve kalem taşır. | `/static/characters/papatya.png` | `/static/characters/voices/papatya.mp3` |
| `kurnaz` | Turuncu-kızıl tüylü, beyaz göğüs lekeli, kabarık kuyruklu bir tilki; boynunda mavi fular, elinde küçük bir büyüteç. | `/static/characters/kurnaz.png` | `/static/characters/voices/kurnaz.mp3` |
| `diken` | Yuvarlak, dikenli ama sevimli görünen küçük bir kirpi; boynunda turuncu-sarı çizgili bir atkı. | `/static/characters/diken.png` | `/static/characters/voices/diken.mp3` |
| `isik` | Küçük, yuvarlak, saydam kanatlı bir ateşböceği; kuyruğunda sıcak sarı-altın bir parıltı. | `/static/characters/isik.png` | `/static/characters/voices/isik.mp3` |

## Mekanlar (6)

| id | İsim | Tür | Açıklama | Görsel | Ambiyans videosu |
| --- | --- | --- | --- | --- | --- |
| `buyuk_mese` | Büyük Meşe Ağacı | Ana Üs / Toplanma Yeri | Ormanın ortasında duran, kovuğunda Zeytin'in yaşadığı, gövdesinde herkesin toplandığı dev bir meşe ağacı. | `/static/locations/buyuk_mese.png` | `/static/locations/videos/buyuk_mese.mp4` |
| `gokkusagi_nehri` | Gökkuşağı Nehri | Doğa / Keşif Alanı | Berrak, ışıltılı bir nehir. Doğa ve bilim temalı bölümler burada geçer. | `/static/locations/gokkusagi_nehri.png` | `/static/locations/videos/gokkusagi_nehri.mp4` |
| `paylasim_bahcesi` | Paylaşım Bahçesi | Topluluk / Aile Alanı | Herkesin birlikte sebze-meyve yetiştirdiği, hasadı paylaştığı ortak bahçe. | `/static/locations/paylasim_bahcesi.png` | `/static/locations/videos/paylasim_bahcesi.mp4` |
| `yildiz_tepesi` | Yıldız Tepesi | Akşam / Kapanış Alanı | Ormanın en yüksek noktası, gece yıldızların net göründüğü bir tepe. Bölümler burada kapanır. | `/static/locations/yildiz_tepesi.png` | `/static/locations/videos/yildiz_tepesi.mp4` |
| `gizli_magara` | **Gizli Mağara** *(yeni)* | Keşif / Gizem Alanı | Duvarlarında parıldayan kristallerin olduğu, sıcak ve büyülü ışıkla aydınlanan, korkutucu olmayan küçük bir mağara. | `/static/locations/gizli_magara.png` | `/static/locations/videos/gizli_magara.mp4` |
| `renkli_cayir` | **Renkli Çayır** *(yeni)* | Sanat / Yaratıcılık Alanı | Her renkten kır çiçeğinin açtığı, kelebeklerin uçuştuğu, canlı ve ilham verici bir çayır. | `/static/locations/renkli_cayir.png` | `/static/locations/videos/renkli_cayir.mp4` |

## Temalar (28)

| theme_id | Etiket | Ana Karakter | Destek Karakter | Mekan |
| --- | --- | --- | --- | --- |
| `paylasma` | Paylaşma | Fındık | Boncuk | Paylaşım Bahçesi |
| `arkadaslik` | Arkadaşlık | Minik | Fındık | Büyük Meşe Ağacı |
| `yardimlasma` | Yardımlaşma | Boncuk | Papatya | Büyük Meşe Ağacı |
| `aile` | Aile Sevgisi | Boncuk | Zeytin | Paylaşım Bahçesi |
| `cesaret` | Cesaret | Minik | Zeytin | Gökkuşağı Nehri |
| `takim_calismasi` | Takım Çalışması | Papatya | Fındık | Gökkuşağı Nehri |
| `sayilar` | Sayılar ve Matematik | Papatya | Minik | Paylaşım Bahçesi |
| `doga_bilim` | Doğa ve Bilim | Zeytin | Papatya | Gökkuşağı Nehri |
| `duygular` | Duyguları Tanımak | Minik | Boncuk | Yıldız Tepesi |
| `durustluk` | Dürüstlük | Zeytin | Fındık | Büyük Meşe Ağacı |
| `sabir` | Sabır | Papatya | Zeytin | Paylaşım Bahçesi |
| `nezaket` | Nezaket | Fındık | Minik | Büyük Meşe Ağacı |
| `ozguven` | Özgüven | Minik | Papatya | Yıldız Tepesi |
| `sorumluluk` | Sorumluluk | Boncuk | Fındık | Büyük Meşe Ağacı |
| `empati` | Empati | Zeytin | Minik | Yıldız Tepesi |
| `duzen` | Düzen ve Temizlik | Papatya | Boncuk | Büyük Meşe Ağacı |
| `saglikli_beslenme` | Sağlıklı Beslenme | Fındık | Papatya | Paylaşım Bahçesi |
| `cevre_sevgisi` | Doğayı Koruma | Zeytin | Boncuk | Gökkuşağı Nehri |
| `yaraticilik` | Yaratıcılık | Boncuk | Minik | Gökkuşağı Nehri |
| `farkliliklara_saygi` | Farklılıklara Saygı | Fındık | Zeytin | Paylaşım Bahçesi |
| `yaratici_dusunme` | **Yaratıcı Düşünme** *(yeni)* | Kurnaz | Papatya | Gizli Mağara |
| `kendini_kabul` | **Kendini Kabul Etme** *(yeni)* | Diken | Minik | Renkli Çayır |
| `umut` | **Umut** *(yeni)* | Işık | Boncuk | Yıldız Tepesi |
| `degisime_uyum` | **Değişime Uyum Sağlama** *(yeni)* | Kurnaz | Zeytin | Gökkuşağı Nehri |
| `sanatsal_ifade` | **Sanatsal İfade** *(yeni)* | Papatya | Diken | Renkli Çayır |
| `korkuyla_basetme` | **Korkuyla Baş Etme** *(yeni)* | Diken | Minik | Gizli Mağara |
| `liderlik` | **Liderlik ve Sorumluluk Alma** *(yeni)* | Kurnaz | Boncuk | Büyük Meşe Ağacı |
| `dostluk_cesitliligi` | **Farklı Arkadaşlıklar Kurmak** *(yeni)* | Işık | Fındık | Gökkuşağı Nehri |

İlk 20 satırın "ders" metinleri için `content_bank.py`'deki `_THEMES` sabitine
bakın; her tema, `EpisodeGeneratorService` tarafından üretilen 5 sahnelik
senaryonun "Çözüm" sahnesinde bu dersi karaktere söyletir.

## Yeni 8 tema için önerilen YouTube SEO anahtar kelimeleri

`episode_seo.py`'deki `EpisodeSeoService`, her üretilen bölüm için etiketleri
(başlık/karakter adından) otomatik türetir — temalar için ayrı, statik bir
"anahtar kelime" alanı content_bank'te tutulmuyor. Aşağıdaki liste, bu 8 yeni
temayla bölüm yayınlayacak bir içerik üreticisi için ek, elle seçilmiş
SEO önerisi niteliğindedir (YouTube başlık/açıklama/etiket alanlarına elle
eklenebilir):

| theme_id | Önerilen anahtar kelimeler |
| --- | --- |
| `yaratici_dusunme` | yaratıcı düşünme, problem çözme, çocuklar için yaratıcılık, kurnaz tilki, farklı düşünme, eğitici çizgi film |
| `kendini_kabul` | kendini kabul etme, özgüven, farklı olmak güzeldir, kirpi karakter, çocuk psikolojisi, değerler eğitimi |
| `umut` | umut, karanlıktan korkmama, ateşböceği, umut ışığı, çocuklar için motivasyon, iyi geceler hikayesi |
| `degisime_uyum` | değişime uyum, yeni durumlar, değişimi kabullenme, esneklik, çocuk gelişimi, duygusal dayanıklılık |
| `sanatsal_ifade` | sanatsal ifade, çocuklar için sanat, yaratıcılık, resim şarkı dans, kendini ifade etme, eğitici çizgi film |
| `korkuyla_basetme` | korkuyla baş etme, cesaret, mağara macerası, çocuk korkuları, kirpi tavşan, duygusal güçlenme |
| `liderlik` | liderlik, sorumluluk alma, takım yönetimi, dinleyerek liderlik, çocuklar için liderlik, karakter eğitimi |
| `dostluk_cesitliligi` | farklı arkadaşlıklar, çeşitlilik, hoşgörü, beklenmedik dostluklar, ateşböceği sincap, çocuklar için empati |
