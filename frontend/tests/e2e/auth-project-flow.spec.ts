import { expect, test } from '@playwright/test'

function uniqueSuffix(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

test('register, generate an episode, save it to a project, and see it on /projects', async ({
  page,
}) => {
  const suffix = uniqueSuffix()
  const email = `e2e-${suffix}@example.com`
  const password = 'correct-horse-battery-1'
  const projectName = `E2E Project ${suffix}`

  await page.goto('/register')
  await page.getByLabel('E-posta').fill(email)
  await page.getByLabel('Şifre').fill(password)
  await page.getByRole('button', { name: 'Kayıt Ol' }).click()
  await expect(page).toHaveURL(/\/projects$/)

  await page.getByLabel('Yeni proje adı').fill(projectName)
  await page.getByRole('button', { name: 'Proje Oluştur' }).click()
  await expect(page.getByRole('heading', { name: projectName })).toBeVisible()

  // Client-side navigation (clicking the nav link) rather than page.goto(),
  // which would force a full page reload and re-fetch Vite's whole dev-server
  // module graph — unrealistic for how a user actually moves through the SPA
  // and noticeably slower.
  await page.getByRole('link', { name: 'Neşeli Orman' }).click()
  await expect(page.getByRole('radiogroup', { name: 'Tema seç' })).toBeVisible()
  await page.getByLabel(`Bu bölümü projeme kaydet (${projectName})`).check()
  await page.getByRole('button', { name: 'Bölüm Üret' }).click()
  await expect(page.getByRole('heading', { name: 'Sahneler' })).toBeVisible({ timeout: 15_000 })

  await page.getByRole('link', { name: 'Projects' }).click()
  const projectCard = page.locator('li', { has: page.getByRole('heading', { name: projectName }) })
  await expect(projectCard).toBeVisible()
  await expect(projectCard.getByText('Neşeli Orman:')).toBeVisible()
})

test('logging out clears the session and hides project-only content', async ({ page }) => {
  const suffix = uniqueSuffix()
  const email = `e2e-logout-${suffix}@example.com`
  const password = 'correct-horse-battery-1'

  await page.goto('/register')
  await page.getByLabel('E-posta').fill(email)
  await page.getByLabel('Şifre').fill(password)
  await page.getByRole('button', { name: 'Kayıt Ol' }).click()
  await expect(page).toHaveURL(/\/projects$/)

  await page.getByRole('button', { name: 'Çıkış Yap' }).click()
  await expect(page.getByRole('link', { name: 'Giriş Yap' })).toBeVisible()

  await page.getByRole('link', { name: 'Projects' }).click()
  await expect(page.getByText('giriş yapmalısın')).toBeVisible()
})
