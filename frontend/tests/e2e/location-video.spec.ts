import { expect, test } from '@playwright/test'

test('the theme picker renders each location as a looping ambient video', async ({ page }) => {
  await page.goto('/episodes')
  await expect(page.getByRole('radiogroup', { name: 'Tema seç' })).toBeVisible()

  const firstCard = page.getByRole('radio').first()
  await expect(firstCard.locator('video')).toHaveAttribute(
    'src',
    /\/static\/locations\/videos\/[a-z_]+\.mp4$/,
  )
})

test('the generated episode summary renders the location as an ambient video too', async ({
  page,
}) => {
  await page.goto('/episodes')
  await page.getByRole('button', { name: 'Bölüm Üret' }).click()
  await expect(page.getByRole('heading', { name: 'Sahneler' })).toBeVisible()

  // Scoped to the "Mekan" (location) block specifically, extending the
  // "Ana Karakter" scoping pattern from voice-samples.spec.ts by one more
  // ancestor level: unlike the voice-sample button (nested inside <dd>),
  // the location video is a sibling of the <dt>/<dd> wrapper, not a
  // descendant of it.
  const locationBlock = page.locator('dt', { hasText: 'Mekan' }).locator('../..')
  await expect(locationBlock.locator('video')).toHaveAttribute(
    'src',
    /\/static\/locations\/videos\/[a-z_]+\.mp4$/,
  )
})
