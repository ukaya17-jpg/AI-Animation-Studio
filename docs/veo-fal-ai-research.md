# Google Veo / fal.ai Araştırma Raporu

Tarih: 2026-07-30

## Sonuç

Google Veo, fal.ai üzerinden standart bir `FAL_KEY` API anahtarıyla
erişilebiliyor; Vertex AI/GCP servis hesabı zorunlu değil. Bu nedenle mevcut
bulgu "yalnızca GCP servis hesabı" karar eşiğine girmemektedir.

fal.ai'nin güncel Veo 3.1 Fast uç noktası `fal-ai/veo3.1/fast` olarak
belgelenmiştir. Metinden videoya istekler 720p veya 1080p, 16:9 ya da 9:16,
24 FPS ve 5--8 saniye aralığını destekler. Kimlik doğrulaması `FAL_KEY` ile
yapılır. [fal.ai API dokümantasyonu](https://fal.ai/models/fal-ai/veo3.1/fast/api)

## Maliyet ve güvenli deneme

Fast katmanında 720p/1080p için ses kapalı maliyet saniye başına $0.10, sesli
maliyet $0.15'tir. En düşük gerçek deneme 5 saniye ve sessiz olduğunda tahmini
$0.50'dır. Bu maliyet, API anahtarı sahibi tarafından açıkça yetkilendirilmeden
harcanmamalıdır. [fal.ai Veo 3.1 model sayfası](https://fal.ai/models/fal-ai/veo3.1)

Önerilen ilk istek:

```json
{
  "prompt": "A five-second static wide shot of a paper windmill turning gently in a sunny classroom, no people, no audio.",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "duration": "5s",
  "audio": false
}
```

Bu rapor sırasında gerçek API isteği yapılmadı: çalışma alanında `FAL_KEY`
yoktu. Gerçek API çağrısı sayacı: **0/8**.

## Bu repodaki entegrasyon durumu

- Hailuo veya başka bir video sağlayıcı adaptörü yok.
- `app/providers` / `app/adapters` sınırları mimaride gelecekteki entegrasyon
  alanı olarak belirtilmiş, fakat uygulama kodu yok.
- `fal_client` ya da bir HTTP video sağlayıcı bağımlılığı yok.
- `deploy.sh` bulunmuyor; bu yüzden backend entegrasyonundan sonra istenen
  dağıtım kontrolü yerine getirilemez.

Bu eksikler yüzünden "Hailuo ile aynı" entegrasyon biçimi doğrulanamıyor.
Varsayıma dayalı üretim kodu eklenmedi. Güvenli sonraki adım, bir `FAL_KEY`
sağlamak, beklenen video-job/polling sözleşmesini tanımlamak ve bir dağıtım
komutu/çalışma kitabı sağlamaktır.

## Kaynaklar

- [fal.ai Veo 3.1 Fast API](https://fal.ai/models/fal-ai/veo3.1/fast/api)
- [fal.ai Veo 3.1 model ve fiyatlandırma](https://fal.ai/models/fal-ai/veo3.1)
- [Google Vertex AI Veo kimlik doğrulama rehberi](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-text)
