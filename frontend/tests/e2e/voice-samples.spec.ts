import { expect, test } from '@playwright/test'

test('clicking a character "listen" button targets that character\'s voice sample, without selecting the theme', async ({
  page,
}) => {
  await page.goto('/episodes')
  await expect(page.getByRole('radiogroup', { name: 'Tema seç' })).toBeVisible()

  const cards = page.getByRole('radio')
  const secondCard = cards.nth(1)
  await expect(secondCard).toHaveAttribute('aria-checked', 'false')

  const voiceButtonWrapper = secondCard.locator('span.inline-flex').first()
  await voiceButtonWrapper.getByRole('button').click()

  await expect(voiceButtonWrapper.locator('audio')).toHaveAttribute(
    'src',
    /\/static\/characters\/voices\/[a-z]+\.mp3$/,
  )
  // Clicking "listen" stops propagation, so it must not also select the card's theme.
  await expect(secondCard).toHaveAttribute('aria-checked', 'false')
})

test('the generated episode summary links each character to their voice sample', async ({
  page,
}) => {
  await page.goto('/episodes')
  await page.getByRole('button', { name: 'Bölüm Üret' }).click()
  await expect(page.getByRole('heading', { name: 'Sahneler' })).toBeVisible()

  // Scoped to the "Ana Karakter" (lead character) block specifically — the
  // theme picker above also renders "listen" buttons, so an unscoped
  // getByRole('button', { name: /sesini dinle/ }).first() could match those
  // instead of the freshly generated episode's summary.
  const leadCharacterBlock = page.locator('dt', { hasText: 'Ana Karakter' }).locator('..')
  await leadCharacterBlock.getByRole('button', { name: /sesini dinle/ }).click()
  await expect(leadCharacterBlock.locator('audio')).toHaveAttribute(
    'src',
    /\/static\/characters\/voices\/[a-z]+\.mp3$/,
  )
})
