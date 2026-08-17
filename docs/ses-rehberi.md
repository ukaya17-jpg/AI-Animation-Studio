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

- **Sağlayıcı (provider):** `artlist`
- **Model:** Eleven v3 (metinden-konuşmaya, Türkçe)

Ses seçimleri, her karakterin `content_bank.py`'deki `VoiceProfile` alanındaki
(`pitch`/`pace`/`tone`/`catchphrase`) betimsel ses notlarıyla eşleşecek şekilde
yapıldı — örneğin Zeytin'in "sakin, öğretmen edası" tonu Mentor sesiyle,
Fındık'ın "tiz-ince, hızlı, çocuksu" tonu Curiosity sesiyle örtüşüyor.

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
