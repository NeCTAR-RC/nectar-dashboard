import { test, expect } from '../../../support/fixtures';
import {
  FORM_URL,
  acceptDialogsOnce,
  byId,
  expandPanel,
  openForm,
  openPanels,
} from './helpers';

// Client-side form behaviour (form-nav.js, data-classification.js).
// Nothing is submitted.
test.beforeEach(async ({ page }) => {
  acceptDialogsOnce(page);
  await openForm(page);
});

test.describe('New Request form: client-side behaviour', () => {
  test('X1 Client-side form-nav behaviour', async ({ page }) => {
    // On load: panel 1 open in step 1, and panelBundle already open in the
    // hidden step 2.
    expect(await openPanels(page, 'request_accordion')).toEqual(['panelOne']);
    expect(await openPanels(page, 'resources_accordion')).toEqual(['panelBundle']);
    await expect(page.locator('section#form-step2')).toBeHidden();
    await expect(page.locator('#form-step-title')).toHaveText('About the Project');

    // 'Next' in panel 1 opens panel 2 and closes panel 1.
    await page.locator('#panelOne .step-nav a', { hasText: 'Next' }).click();
    await expect(page.locator('#panelTwo')).toBeVisible();
    await expect(page.locator('#panelOne')).toBeHidden();
    await expect.poll(() => openPanels(page, 'request_accordion')).toEqual(['panelTwo']);
    await expect(page.locator('#request_accordion > .panel:has(#panelTwo)')).toHaveClass(
      /panel-primary/,
    );

    // 'Previous' goes back.
    await page.locator('#panelTwo .step-nav a', { hasText: 'Previous' }).click();
    await expect(page.locator('#panelOne')).toBeVisible();
    await expect.poll(() => openPanels(page, 'request_accordion')).toEqual(['panelOne']);

    // The STEP 2 tab swaps the sections and sets the hash.
    await page.locator('#allocation_form_nav a[href="#form-step2"]').click();
    await expect(page.locator('section#form-step1')).toBeHidden();
    await expect(page.locator('section#form-step2')).toBeVisible();
    await expect(page.locator('#panelBundle')).toBeVisible();
    await expect(page.locator('#form-step-title')).toHaveText('Cloud Resources');
    await expect(page).toHaveURL(/\/allocation\/#!#form-step2$/);

    // A reload with that hash opens step 2 directly.
    await page.reload();
    await expect(page.locator('section#form-step2')).toBeVisible();
    await expect(page.locator('section#form-step1')).toBeHidden();

    // No client-side check blocks step 2 or Submit on an empty form: the
    // form has novalidate and all validation is server side (see V1, V9
    // for where server errors open panels and steps).
    await expect(page.locator('form#new-allocation')).toHaveAttribute('novalidate', 'novalidate');
    await expect(page.locator('form#new-allocation')).toHaveAttribute('action', FORM_URL);
    await expect(page.locator('form#new-allocation')).toHaveAttribute('method', 'post');
    await expect(page.locator('#submit-section input[type=submit]')).toBeEnabled();
    // Some fields carry the HTML required attribute, but novalidate means
    // the browser never enforces it.
    await expect(page.locator('#new-allocation [required]')).toHaveCount(6);
  });

  test('X2 Sensitive-data client behaviour', async ({ page }) => {
    await expandPanel(page, 'panelTwo');
    const sensitive = byId(page, 'id_has_sensitive_data');
    const level = byId(page, 'id_data_classification_level');
    const hidden = byId(page, 'id_data_classification_level_hidden');
    const green = level.locator('option[value="green"]');
    const review = page.locator('#institutional_data_review_container');
    const box = page.locator('#data-classification-box');
    const reviewAsterisk = page.locator(
      'label[for="id_institutional_data_review"] .glyphicon-asterisk',
    );

    // On load: unset and enabled, but the Green option is already
    // disabled; the review field is hidden.
    await expect(level).toHaveValue('');
    await expect(level).toBeEnabled();
    await expect(green).toBeDisabled();
    await expect(review).toBeHidden();
    await expect(box).toBeHidden();

    // No sensitive data: forced to Green and locked.
    await sensitive.selectOption('no_sensitive');
    await expect(level).toHaveValue('green');
    await expect(level).toBeDisabled();
    await expect(hidden).toHaveValue('green');
    await expect(review).toBeHidden();
    await expect(box).toBeVisible();
    await expect(box).toHaveText('Data misuse would have little to no impact.');

    // Sensitive: Green is cleared and disabled; the review field appears
    // and gains a required marker.
    await sensitive.selectOption('sensitive');
    await expect(level).toHaveValue('');
    await expect(level).toBeEnabled();
    await expect(green).toBeDisabled();
    await expect(hidden).toHaveValue('');
    await expect(review).toBeVisible();
    await expect(reviewAsterisk).toHaveCount(1);
    await level.selectOption('red');
    await expect(hidden).toHaveValue('red');
    await expect(box).toBeVisible();
    await expect(box).toContainText('Data breach or misuse is expected to cause severe harm');

    // Unsure: forced to Not Sure and locked; review hidden and reset.
    await byId(page, 'id_institutional_data_review').selectOption('yes');
    await sensitive.selectOption('unknown');
    await expect(level).toHaveValue('not_sure');
    await expect(level).toBeDisabled();
    await expect(hidden).toHaveValue('not_sure');
    await expect(review).toBeHidden();
    await expect(byId(page, 'id_institutional_data_review')).toHaveValue('');

    // Back to 'Please select...': unlocked, value kept.
    await sensitive.selectOption('');
    await expect(level).toHaveValue('not_sure');
    await expect(level).toBeEnabled();
    await expect(green).toBeDisabled();

    // Multiple allocations 'Yes' hides the three estimate fields.
    const estimates = page.locator('#panelTwo .toggleable');
    await expect(estimates).toHaveCount(3);
    for (const i of [0, 1, 2]) {
      await expect(estimates.nth(i)).toBeVisible();
    }
    await byId(page, 'id_multiple_allocations_check').selectOption('True');
    for (const i of [0, 1, 2]) {
      await expect(estimates.nth(i)).toBeHidden();
    }
    await byId(page, 'id_multiple_allocations_check').selectOption('False');
    for (const i of [0, 1, 2]) {
      await expect(estimates.nth(i)).toBeVisible();
    }
  });
});
