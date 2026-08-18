import { expect, test } from '@playwright/test'

test('downloading the production package ZIP from the episode detail view and the history list', async ({
  page,
}) => {
  await page.goto('/episodes')
  await page.getByRole('button', { name: 'Bölüm Üret' }).click()
  await expect(page.getByRole('heading', { name: 'Sahneler' })).toBeVisible()

  // Scoped with a real <button> locator (not getByRole) so it can't also match
  // the history-list card's outer role="button" <div>, whose computed
  // accessible name includes its nested export button's label too.
  const detailExportButton = page
    .locator('button', { hasText: '📦 Prodüksiyon Paketini İndir' })
    .first()
  const detailDownloadPromise = page.waitForEvent('download')
  await detailExportButton.click()
  const detailDownload = await detailDownloadPromise
  expect(detailDownload.suggestedFilename()).toMatch(/-produksiyon-paketi\.zip$/)

  // The same episode also now appears as the newest card in the history list
  // below; its own export button should trigger a download too. Scoped off
  // the "Geçmiş Bölümler" heading, extending the ancestor-navigation pattern
  // from location-video.spec.ts.
  const historySection = page.locator('h2', { hasText: 'Geçmiş Bölümler' }).locator('..')
  const historyExportButton = historySection
    .locator('li')
    .first()
    .locator('button', { hasText: '📦 Prodüksiyon Paketini İndir' })
  const historyDownloadPromise = page.waitForEvent('download')
  await historyExportButton.click()
  const historyDownload = await historyDownloadPromise
  expect(historyDownload.suggestedFilename()).toMatch(/-produksiyon-paketi\.zip$/)
})
