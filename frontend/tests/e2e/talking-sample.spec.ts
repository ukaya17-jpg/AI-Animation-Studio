import { expect, test } from '@playwright/test'

test('Kurnaz\'s theme card shows a talking-sample button that plays without selecting the theme', async ({
  page,
}) => {
  await page.goto('/episodes')
  await expect(page.getByRole('radiogroup', { name: 'Tema seç' })).toBeVisible()

  // "Yaratıcı Düşünme" is one of the themes where Kurnaz leads and is currently
  // the only character with a talking-sample demo video (see docs/ses-rehberi.md).
  const kurnazCard = page.getByRole('radio').filter({ hasText: 'Yaratıcı Düşünme' })
  await expect(kurnazCard).toHaveAttribute('aria-checked', 'false')

  const talkingSampleButton = kurnazCard.getByRole('button', {
    name: 'Canlandırılmış Örneği Gör',
  })
  await expect(talkingSampleButton).toBeVisible()
  await talkingSampleButton.click()

  // Clicking the badge stops propagation, so it must not also select the theme card.
  await expect(kurnazCard).toHaveAttribute('aria-checked', 'false')

  const dialog = page.getByRole('dialog', { name: /Kurnaz canlandırılmış örnek videosu/ })
  await expect(dialog).toBeVisible()
  await expect(dialog.locator('video')).toHaveAttribute(
    'src',
    '/static/characters/talking_samples/kurnaz_demo.mp4',
  )

  await dialog.getByRole('button', { name: 'Kapat' }).click()
  await expect(dialog).not.toBeVisible()
})

test('a theme without a talking sample renders no talking-sample button', async ({ page }) => {
  await page.goto('/episodes')
  await expect(page.getByRole('radiogroup', { name: 'Tema seç' })).toBeVisible()

  const paylasmaCard = page.getByRole('radio').filter({ hasText: 'Paylaşma' })
  await expect(
    paylasmaCard.getByRole('button', { name: 'Canlandırılmış Örneği Gör' }),
  ).toHaveCount(0)
})
