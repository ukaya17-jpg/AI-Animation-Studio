# Overnight Progress

## OTONOM KARAR — 2026-07-30

- Çalışma alanı başlangıçta `main` üzerinde `.gitignore` değişik ve proje
  dosyalarının tamamı izlenmeyen durumdaydı. Kullanıcının mevcut çalışmalarını
  sahiplenmemek için sadece bu gece oluşturulan veya açıkça değiştirilen dosyalar
  commit'e alınacaktır.
- İstenen ayrı dal ile `git push origin main` birbiriyle çelişmektedir. Değişikliği
  güvenli ve geri alınabilir tutmak için commit'ler
  `overnight/topic-fix-and-followups` dalına pushlanacaktır; `main` doğrudan
  değiştirilmeyecektir.

## Görev 1 — Senaryo-Konu Uyumsuzluğu

**Durum: BLOKE — uygulamada araştırma, outline, LLM/"Stok Üretim" promptu,
script üretimi veya herhangi bir AI sağlayıcı entegrasyonu yok.**

Kanıt: kaynak taraması yalnızca Sprint 2'nin yerel storyboard üreticisini buldu;
`research`, `outline`, `stock production`/`Stok Üretim`, sağlayıcı API anahtarı ve
gerçek API çağrısı yapan kod bulunmuyor. Bu nedenle istenen kök neden ve öncesi/
sonrası gerçek API karşılaştırması mevcut çalışma alanında gerçekleştirilemez.
Yanlış bir üretim hattı varsayarak kod değiştirmedim.

Gerçek API çağrısı sayacı: **0/8**. Mevcut kaynak ağacında gerçek API ile
öncesi/sonrası karşılaştırılacak bir üretim hattı veya kimlik bilgisi yoktur.

## Görev 2 — "Video Konusu" etiketi

**Durum: Atlandı — frontend yalnızca Sprint 1 placeholder sayfalarından oluşuyor;
"Video Konusu" veya ilgili bir form/etiket bulunmuyor.**

## Görev 3 — Google Veo araştırması

**Durum: Araştırma tamamlandı, entegrasyon önkoşulu eksik.**

fal.ai Veo 3.1 Fast API'si `FAL_KEY` ile kullanılabiliyor; Vertex AI/GCP servis
hesabı zorunlu değil. Ancak çalışma alanında Hailuo/sağlayıcı adaptörü yok,
`FAL_KEY` mevcut değil ve gerçek API testi için maliyet yetkisi yok. Canlı istek
sayacı: **0/8**. Ayrıntılar `docs/veo-fal-ai-research.md` içindedir.

## OTONOM KARAR — Veo

Mevcut olmayan bir "Hailuo deseni" ve API anahtarı varsayarak yeni bir video
sağlayıcı mimarisi eklemedim. En muhafazakâr geri alınabilir seçenek olarak,
kanıtlı araştırma raporu hazırlandı; canlı maliyet oluşmadı.

## Görev 4 — Genel sağlık kontrolü

**Durum: Tamamlandı (dağıtım doğrulaması engelli).**

- Backend: `DEBUG=false .venv/bin/pytest -q` → **17 passed**
- Backend: `.venv/bin/ruff check .` → **All checks passed**
- Backend: `.venv/bin/mypy app` → **Success: no issues found in 37 source files**
- Frontend: `npm run lint` → **başarılı**
- Frontend: `npm run build` → **başarılı**
- `./deploy.sh` iki kez denendi; çalışma alanında dosya bulunmadığı için
  production dağıtımı/çalışan servis sağlığı doğrulanamadı.

### Test altyapısı düzeltmesi

Başlangıçta sanal ortamda bağımlılıklar kurulmamıştı. Projenin `dev` bağımlılıkları
kuruldu. Test sırasında platformdaki senkron FastAPI dependency thread-pool'u
kilitlendiği için saf nesne kuran bağımlılıklar async hale getirildi; HTTP testleri
platformdan bağımsız ASGI transport kullanacak şekilde güncellendi. FastAPI sürüm
aralığı uyumlu `0.115–0.120` bandına daraltıldı.

## Yayınlama engeli

`gh --version` komutu `gh: command not found` sonucu verdi. Yayınlama becerisinin
zorunlu önkoşulu olan GitHub CLI ve doğrulanmış oturum yok; bu nedenle commit/push
ve PR oluşturma gerçekleştirilemedi. Dal başarıyla oluşturuldu:
`overnight/topic-fix-and-followups`.
