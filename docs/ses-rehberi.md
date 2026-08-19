# Ses Rehberi

Neşeli Orman karakterlerinin Türkçe ses örnekleri, [Artlist](https://artlist.io)
üzerinden Eleven v3 modeliyle üretildi ve `backend/app/static/characters/voices/`
altında statik dosya olarak projeye kalıcı şekilde eklendi (görsellerle aynı
desen — `backend/app/static/characters/*.png`).

Bu dosya, gelecekte tam bölüm seslendirmesi (her sahnenin diyaloğunun
otomatik seslendirilmesi) otomatikleştirilmek istendiğinde hangi Artlist
sesinin hangi karaktere karşılık geldiğini bulmak için referans niteliğindedir.

## Karakter → ses eşlemesi

| Karakter | Ses dosyası | Artlist sesi | voiceId | Cinsiyet / yaş grubu |
| --- | --- | --- | --- | --- |
| Zeytin | `voices/zeytin.mp3` | Mentor | 30 | MALE, MIDDLE_AGED |
| Fındık | `voices/findik.mp3` | Curiosity | 47 | MALE, CHILD |
| Minik | `voices/minik.mp3` | Cupcake | 87 | FEMALE, CHILD |
| Boncuk | `voices/boncuk.mp3` | Gravity | 113130 | MALE, MIDDLE_AGED |
| Papatya | `voices/papatya.mp3` | Bright | 32 | FEMALE, YOUNG_ADULT |
| Kurnaz | `voices/kurnaz.mp3` | Wit | 25 | MALE, MIDDLE_AGED |
| Diken | `voices/diken.mp3` | Mild | 43 | MALE, YOUNG_ADULT |
| Işık | `voices/isik.mp3` | Serenity | 29 | FEMALE, ADULT |

- **Sağlayıcı (provider):** `artlist`
- **Model:** Eleven v3 (metinden-konuşmaya, Türkçe)

Ses seçimleri, her karakterin `content_bank.py`'deki `VoiceProfile` alanındaki
(`pitch`/`pace`/`tone`/`catchphrase`) betimsel ses notlarıyla eşleşecek şekilde
yapıldı — örneğin Zeytin'in "sakin, öğretmen edası" tonu Mentor sesiyle,
Fındık'ın "tiz-ince, hızlı, çocuksu" tonu Curiosity sesiyle örtüşüyor. Aynı
mantıkla: Kurnaz'ın "orta-kalın, esprili, kendinden emin" tonu Wit sesiyle,
Diken'in "yumuşak, tereddütlü, çekingen ama sıcak" tonu Mild sesiyle, Işık'ın
"yumuşak, sakin, umut verici" tonu ise Serenity sesiyle örtüşüyor.

## API'de nerede kullanılıyor

`voice_sample_url` alanı şu yanıtlarda mevcut:

- `GET /episodes/themes` → `lead_character_voice_sample_url`,
  `support_character_voice_sample_url`
- `GET /episodes`, `GET /episodes/{id}` (liste özeti) →
  `lead_character_voice_sample_url`, `support_character_voice_sample_url`
- `POST /episodes/generate`, `GET /episodes/{id}` (tam detay) →
  `episode.lead_character.voice_sample_url`,
  `episode.support_character.voice_sample_url`

Frontend'de `ThemePicker` ve `EpisodeSummary` bileşenleri bu URL'leri bir
"▶ Sesini dinle" butonuyla çalıyor (`<audio>` elementi, ek bir player
kütüphanesi kullanılmadı).

## Gelecekteki tam bölüm seslendirmesi için not

Şu an her karakter için sadece TEK bir kısa örnek ses klibi var (tanıtım
amaçlı). Tam bölüm seslendirmesi (her sahnenin diyaloğunun ayrı ayrı
seslendirilmesi) otomatikleştirilmek istenirse:

1. Yukarıdaki `voiceId`'ler Artlist'in `generate_voiceover`/TTS API'sine
   sahne diyaloglarıyla birlikte geçilebilir.
2. Bu, yeni bir dış servis çağrısı (ve muhtemelen bir API anahtarı/kredi
   maliyeti) gerektirir — bu rehber sadece referans bilgisidir, otomatik bir
   entegrasyon bu oturumda yapılmadı.

## Konuşan Karakter Videosu (Dudak Senkronu) — Maliyet Notu

Artlist'in "Seedance 2.5" modeli (modelId 3002, multi-to-video özelliği),
bir karakter görseli + bir ses dosyası referans alarak o karakterin
gerçekten o sesle konuştuğu, dudak senkronlu bir video üretebiliyor.

**Maliyet:** ~500 kredi/saniye video (6 saniyelik bir klip ≈ 3.000 kredi).
Karşılaştırma: statik görsel ≈ 160 kredi, ambient mekan videosu ≈ 750
kredi/5sn. Yani dudak senkronlu konuşma, en pahalı üretim türü.

**Kritik nokta — stil kilidi gerekli:** Prompt'ta görsel stili açıkça
zorlamazsan (düz vektör/2D çizgi film), model karakteri fotogerçekçi/3D
bir görünüme çeviriyor — bu, kanalın görsel kimliğini bozar. Çalışan
prompt formülü:

> "STYLE LOCK: flat 2D vector cartoon illustration, exactly matching the
> input reference image's art style — simple flat colors, bold clean
> black outlines, NO 3D rendering, NO photorealism... [karakter+konuşma
> tarifi]... Character design, proportions, colors and line style must
> stay IDENTICAL to the reference image — only the mouth/eyes animate."

**Bütçe gerçeği:** 28 bölümlük bir seride, ortalama bölüm başına ~8-10
konuşma repliği olsa, tam animasyon için gereken kredi tüm aylık planı
(16.500 kredi) çok aşar. Bu yöntem şu an sadece "vitrin/tanıtım" amaçlı
kullanılabilir, tam otomatik bölüm animasyonu için değil — ya çok daha
büyük bir kredi bütçesi ya da farklı (muhtemelen daha ucuz) bir üretim
yöntemi gerekir.

**Mevcut durum:** Bu yöntemle şu an SADECE Kurnaz için tek bir demo video
üretildi — `backend/app/static/characters/talking_samples/kurnaz_demo.mp4`
(bütçe yetersizliği nedeniyle diğer 7 karaktere sistematik olarak
uygulanmadı). `EpisodeCharacter` dataclass'ında (`app/models/episode_cast.py`)
opsiyonel bir `talking_sample_url: str | None = None` alanı var; sadece
Kurnaz'ın `content_bank.py`'deki kaydında dolu, diğer 7 karakterde `None`.

`GET /episodes/themes` yanıtında `lead_character_talking_sample_url` /
`support_character_talking_sample_url` olarak, null-safe şekilde (dolu
değilse `null`) dışa aktarılıyor. Frontend'de `ThemePicker`, bu alan
doluysa (yalnızca Kurnaz'ın lider olduğu temalarda) karakter avatarlarının
altında küçük bir "🎬 Canlandırılmış Örneği Gör" rozeti gösteriyor;
tıklanınca video bir modal'da oynatılıyor (`TalkingSampleButton` bileşeni).
Tek bölüm/toplu export ZIP'lerine bu video dahil edilmiyor — sadece
uygulama içi bir vitrin özelliği.
