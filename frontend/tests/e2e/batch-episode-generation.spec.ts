import { expect, test } from '@playwright/test'

function uniqueSuffix(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

test('clicking batch-generate on a project shows a loading state, then a download button', async ({
  page,
}) => {
  const suffix = uniqueSuffix()
  const email = `e2e-batch-${suffix}@example.com`
  const password = 'correct-horse-battery-1'
  const projectName = `E2E Batch Project ${suffix}`

  // Both the batch-generate call and the episode list re-fetch it triggers are
  // intercepted, rather than left to hit the real backend. Generating all 20
  // themes for real is fast in this app (pure templating, no external calls —
  // see episode_service.py), but this test only needs to prove the button
  // wires up to the right request, renders a loading state, and reveals the
  // download button once episodes exist — not that backend generation speed
  // stays fast forever, which is what a real 20-episode wait would end up
  // pinning down.
  let batchGenerated = false
  let batchRequestBody: unknown = null

  await page.route('**/episodes/generate-batch', async (route) => {
    batchRequestBody = route.request().postDataJSON()
    await new Promise((resolve) => setTimeout(resolve, 300))
    batchGenerated = true
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        project_id:
          batchRequestBody && typeof batchRequestBody === 'object'
            ? (batchRequestBody as { project_id: string | null }).project_id
            : null,
        created: [
          {
            id: '11111111-1111-1111-1111-111111111111',
            theme_id: 'paylasma',
            theme_label: 'Paylaşma',
            title: 'Neşeli Orman: Paylaşma',
          },
        ],
        skipped_theme_ids: Array.from({ length: 19 }, (_, i) => `tema-${i}`),
      }),
    })
  })

  await page.route('**/episodes?*', async (route) => {
    if (!batchGenerated) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, page: 1, page_size: 100 }),
      })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: '11111111-1111-1111-1111-111111111111',
            project_id: null,
            title: 'Neşeli Orman: Paylaşma',
            theme_id: 'paylasma',
            theme_label: 'Paylaşma',
            lead_character_name: 'Fındık',
            lead_character_image_url: '/static/characters/findik.png',
            lead_character_voice_sample_url: '/static/characters/voices/findik.mp3',
            support_character_name: 'Boncuk',
            support_character_image_url: '/static/characters/boncuk.png',
            support_character_voice_sample_url: '/static/characters/voices/boncuk.mp3',
            location_name: 'Paylaşım Bahçesi',
            location_image_url: '/static/locations/paylasim_bahcesi.png',
            location_ambient_video_url: '/static/locations/videos/paylasim_bahcesi.mp4',
            created_at: new Date().toISOString(),
          },
        ],
        total: 1,
        page: 1,
        page_size: 100,
      }),
    })
  })

  await page.goto('/register')
  await page.getByLabel('E-posta').fill(email)
  await page.getByLabel('Şifre').fill(password)
  await page.getByRole('button', { name: 'Kayıt Ol' }).click()
  await expect(page).toHaveURL(/\/projects$/)

  await page.getByLabel('Yeni proje adı').fill(projectName)
  await page.getByRole('button', { name: 'Proje Oluştur' }).click()
  const projectCard = page.locator('li', { has: page.getByRole('heading', { name: projectName }) })
  await expect(projectCard).toBeVisible()

  // No download button until at least one episode exists for this project.
  await expect(
    projectCard.getByRole('button', { name: '📦 Tüm Bölümleri İndir (ZIP)' }),
  ).toHaveCount(0)

  // The download button only appears once episodes.length > 0 (asserted above
  // that it doesn't exist yet), so this is unambiguously the generate button —
  // located positionally rather than by name, since the click flips its
  // accessible name to the loading label checked right below.
  const generateButton = projectCard.getByRole('button').first()
  await expect(generateButton).toHaveText('🎬 Tüm Temalarla Toplu Üret')
  await generateButton.click()
  await expect(page.getByText('20 bölüm üretiliyor (biraz sürebilir)…')).toBeVisible()
  await expect(generateButton).toBeDisabled()

  await expect(projectCard.getByText(/1 yeni bölüm üretildi/)).toBeVisible()
  expect(batchRequestBody).not.toBeNull()

  await expect(
    projectCard.getByRole('button', { name: '📦 Tüm Bölümleri İndir (ZIP)' }),
  ).toBeVisible()
  await expect(projectCard.getByText('Neşeli Orman: Paylaşma')).toBeVisible()
})
