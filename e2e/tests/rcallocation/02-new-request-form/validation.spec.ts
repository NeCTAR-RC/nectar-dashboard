import { test, expect } from '../../../support/fixtures';
import {
  FIX_ERRORS,
  acceptDialogsOnce,
  byId,
  errorMap,
  fieldErrors,
  fillBaseline,
  openForm,
  openPanels,
  submitExpectingErrors,
} from './helpers';

// Server-side validation of the New Request form.  The values are set
// straight into the form fields (fillBaseline) so each rule is tested on
// its own; the widgets themselves are covered by the R, X and S tests.
//
// Every submit here is built to fail.  The identifier defaults to a fresh
// pwtest- name so an unexpected success is still cleaned up.  Each case is
// its own test: one submit takes 5-20 s while the dev server is shared.
test.beforeEach(async ({ page }) => {
  acceptDialogsOnce(page);
  await openForm(page);
});

const REQUIRED = 'This field is required.';
type Values = Record<string, string | string[]>;
type Errors = Record<string, string[]>;

// The FoR errors render in the NOTE area of panel 3, not beside a field.
const FOR_AREA = '#panelThree .col-xs-12 > .has-error .help-block';

test.describe('New Request form: validation', () => {
  test('V1 Empty form submit: error inventory and placement', async ({ page }) => {
    await submitExpectingErrors(page);

    await expect(page).toHaveTitle('Allocation Request - Nectar Dashboard');
    // The alert sits at the foot of the intro column, beside (not above)
    // the Before-you-begin panel in the right-hand column.
    const columns = page.locator('#allocationrequest_edit > section > .row > .col-md-6');
    await expect(columns.nth(0).locator('.alert-danger')).toHaveText(FIX_ERRORS);
    await expect(columns.nth(1)).toContainText('Before you begin...');

    // Panel 1 stays the only open panel; step 1 stays shown.
    expect(await openPanels(page, 'request_accordion')).toEqual(['panelOne']);
    await expect(page.locator('section#form-step1')).toBeVisible();
    await expect(page.locator('section#form-step2')).toBeHidden();
    // Panels with errors are flagged panel-danger; panel 1 is also primary.
    expect(
      await page
        .locator('#request_accordion > .panel.panel-danger .request-collapse')
        .evaluateAll((els) => els.map((e) => e.id)),
    ).toEqual(['panelOne', 'panelTwo', 'panelThree', 'panelFour', 'panelFive', 'panelSeven']);
    await expect(page.locator('#request_accordion > .panel:has(#panelOne)')).toHaveClass(
      /panel-primary/,
    );

    // No estimate errors: the FoR error aborts clean() before them.
    expect(await errorMap(page)).toEqual({
      project_description: [REQUIRED],
      project_name: [REQUIRED],
      use_case: [REQUIRED],
      has_sensitive_data: [REQUIRED],
      data_classification_level: [REQUIRED],
      FOR: ['Percentage set for unspecified Field Of Research'],
      supported_organisations: [REQUIRED],
      'investigators-0-title': [REQUIRED],
      'investigators-0-given_name': [REQUIRED],
      'investigators-0-surname': [REQUIRED],
      'investigators-0-email': [REQUIRED],
      'investigators-0-primary_organisation': [REQUIRED],
      'grants-0-grant_type': [REQUIRED],
      'grants-0-grant_subtype': [REQUIRED],
      'grants-0-total_funding': [REQUIRED],
      usage_types: ['Please check one or more of the above'],
    });

    // Placement: each error renders inside its owning panel.
    const inPanel = (panel: string) => page.locator(`#${panel} .has-error`);
    await expect(inPanel('panelOne')).toHaveCount(2);
    await expect(inPanel('panelTwo')).toHaveCount(3);
    await expect(inPanel('panelThree')).toHaveCount(1);
    await expect(inPanel('panelFour')).toHaveCount(1);
    await expect(inPanel('panelFive')).toHaveCount(5);
    await expect(inPanel('panelSix')).toHaveCount(0);
    await expect(inPanel('panelSeven')).toHaveCount(3);
    await expect(inPanel('panelJustification')).toHaveCount(1);
    await expect(page.locator(FOR_AREA)).toHaveText([
      'Percentage set for unspecified Field Of Research',
    ]);
  });

  const LETTERS = 'Letters, numbers, underscore and hyphens only. Must start with a letter.';
  const LENGTH = 'Between 5 and 32 characters required.';
  const identifierCases: [string, string, string[]][] = [
    ['too short', 'ab', [LENGTH]],
    ['leading digit', '1abcdef', [LETTERS]],
    ['space and punctuation', 'abc def!', [LETTERS]],
    ['pt- prefix', 'pt-abcdef', ['Must not start with "pt-" or similar.']],
    // Typed input stops at the maxlength of 32; a posted 33-character
    // value fails both the length regex and max_length.
    [
      '33 characters',
      'a'.repeat(33),
      [LENGTH, 'Ensure this value has at most 32 characters (it has 33).'],
    ],
  ];
  for (const [title, name, errors] of identifierCases) {
    test(`V2 Project Identifier: ${title}`, async ({ page }) => {
      await expect(byId(page, 'id_project_name')).toHaveAttribute('maxlength', '32');
      await fillBaseline(page, { project_name: name });
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual({ project_name: errors });
      await expect(byId(page, 'id_project_name')).toHaveValue(name);
      await expect(page.locator('#panelOne .has-error')).toHaveCount(1);
    });
  }

  test('V2 Project Identifier: duplicate of an approved allocation', async ({
    page,
    allocations,
  }) => {
    // Only identifiers with history rows are detected as duplicates (see
    // V5), so reuse an approved allocation's identifier.
    const existing = await allocations.createApproved();
    await fillBaseline(page, { project_name: existing.project_name });
    await submitExpectingErrors(page);
    const DUPLICATE =
      'That project identifier already exists. If your allocation has ' +
      'been approved already, please go here to amend it. Otherwise, ' +
      'choose a different identifier.';
    expect(await errorMap(page)).toEqual({ project_name: [DUPLICATE] });
    await expect(
      fieldErrors(page, 'id_project_name').getByRole('link', { name: 'here' }),
    ).toHaveAttribute('href', '/allocation/user_requests/');
    await expect(page.locator('#panelOne .has-error .help-block')).toHaveText([DUPLICATE]);
  });

  const forCases: [string, Values, string][] = [
    [
      'zero percentage',
      { field_of_research_1: '4601', for_percentage_1: '0' },
      "Percentage for Field Of Research '4601' cannot be 0",
    ],
    [
      'percentage without a code',
      { field_of_research_1: '', for_percentage_1: '50' },
      'Percentage set for unspecified Field Of Research',
    ],
    [
      'sum over 100',
      {
        field_of_research_1: '4601',
        for_percentage_1: '60',
        field_of_research_2: '3101',
        for_percentage_2: '60',
      },
      'Sum of Field Of Research percentages greater than 100',
    ],
  ];
  for (const [title, values, message] of forCases) {
    test(`V3 Fields of Research percentage rules: ${title}`, async ({ page }) => {
      await fillBaseline(page, values);
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual({ FOR: [message] });
      await expect(page.locator(FOR_AREA)).toHaveText([message]);
      await expect(page.locator('#panelThree .controls .has-error')).toHaveCount(0);
    });
  }

  const REVIEW = 'This field is required when the project involves sensitive data';
  const sensitiveCases: [string, Values, Errors][] = [
    [
      'no sensitive data, Red',
      { has_sensitive_data: 'no_sensitive', data_classification_level: 'red' },
      {
        data_classification_level: [
          'Data classification must be Green when project has no sensitive data',
        ],
      },
    ],
    [
      'unsure, Green',
      { has_sensitive_data: 'unknown', data_classification_level: 'green' },
      {
        data_classification_level: [
          'Data classification must be Not Sure when unsure about sensitive data',
        ],
      },
    ],
    [
      'sensitive, Green, no review',
      {
        has_sensitive_data: 'sensitive',
        data_classification_level: 'green',
        institutional_data_review: '',
      },
      {
        data_classification_level: [
          'Data classification cannot be Green when project has sensitive data',
        ],
        institutional_data_review: [REVIEW],
      },
    ],
    [
      'sensitive, Red, no review',
      {
        has_sensitive_data: 'sensitive',
        data_classification_level: 'red',
        institutional_data_review: '',
      },
      { institutional_data_review: [REVIEW] },
    ],
  ];
  for (const [title, values, errors] of sensitiveCases) {
    test(`V4 Sensitive data and classification rules: ${title}`, async ({ page }) => {
      await fillBaseline(page, values);
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual(errors);
      // All of them render in panel 2.
      await expect(page.locator('#panelTwo .has-error')).toHaveCount(Object.keys(errors).length);
    });
  }

  const NO_ESTIMATES = {
    direct_access_user_estimate: '',
    estimated_service_count: '',
    estimated_service_active_users: '',
  };

  test('V5 Usage estimates required unless multiple allocations is Yes: No', async ({
    page,
  }) => {
    await fillBaseline(page, { ...NO_ESTIMATES, multiple_allocations_check: 'False' });
    await submitExpectingErrors(page);
    // 'This field is required' without a full stop.
    expect(await errorMap(page)).toEqual({
      direct_access_user_estimate: ['This field is required'],
      estimated_service_count: ['This field is required'],
      estimated_service_active_users: ['This field is required'],
    });
    await expect(page.locator('#panelTwo .has-error')).toHaveCount(3);
  });

  test('V5 Usage estimates required unless multiple allocations is Yes: Yes', async ({
    page,
    allocations,
  }) => {
    // Guard: reuse an existing identifier so this submit cannot succeed;
    // the only error left must be the duplicate identifier.  It must be an
    // approved allocation: for a new request the duplicate check excludes
    // every row whose parent_request is null (the unsaved instance has no
    // id), so only the history copies an approval creates are matched.  A
    // Submitted (E) identifier is not detected as a duplicate.
    const existing = await allocations.createApproved();
    await fillBaseline(page, {
      ...NO_ESTIMATES,
      multiple_allocations_check: 'True',
      project_name: existing.project_name,
    });
    await submitExpectingErrors(page);
    const errors = await errorMap(page);
    expect(Object.keys(errors)).toEqual(['project_name']);
    expect(errors.project_name[0]).toMatch(/^That project identifier already exists/);
  });

  const supportCases: [string, Values, Errors][] = [
    [
      'ARDC details without a program',
      { ardc_explanation: 'Some detail', ardc_support: [] },
      {
        ardc_explanation: [
          'No ARDC projects or programs have been selected: choose one or more, or remove the explanation text.',
        ],
      },
    ],
    [
      'NCRIS details without a facility',
      { ncris_explanation: 'Some detail', ncris_facilities: [] },
      {
        ncris_explanation: [
          'No NCRIS Facilities have been selected: choose one or more, or remove the explanation text.',
        ],
      },
    ],
    [
      'Pilot without details',
      { ncris_facilities: ['Pilot'], ncris_explanation: '' },
      {
        ncris_explanation: [
          "More details are required when you include 'Pilot' or 'Other' above.",
        ],
      },
    ],
    [
      'ARDC program needing details',
      // 'ARDC Platforms' is flagged explain=true in /rest_api/ardc-projects/.
      { ardc_support: ['ARDC Platforms'], ardc_explanation: '' },
      {
        ardc_explanation: [
          'Add details for the ARDC support that you are claiming for your request.',
        ],
      },
    ],
  ];
  for (const [title, values, errors] of supportCases) {
    test(`V6 ARDC and NCRIS support rules: ${title}`, async ({ page }) => {
      await fillBaseline(page, values);
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual(errors);
      // All render in panel 6.
      await expect(page.locator('#panelSix .has-error')).toHaveCount(1);
    });
  }

  const orgCases: [string, Values, Errors, string][] = [
    [
      "'All Organisations' with another",
      { supported_organisations: '314402,5' },
      {
        supported_organisations: [
          "'All Organisations' should not be used with any other organisation",
        ],
      },
      'panelFour',
    ],
    [
      "CI organisation 'All Organisations'",
      { 'investigators-0-primary_organisation': '314402' },
      {
        'investigators-0-primary_organisation': [
          "'All Organisations' is not meaningful in this context",
        ],
      },
      'panelFive',
    ],
    [
      'CI organisation empty',
      { 'investigators-0-primary_organisation': '' },
      { 'investigators-0-primary_organisation': [REQUIRED] },
      'panelFive',
    ],
  ];
  for (const [title, values, errors, panel] of orgCases) {
    test(`V7 Supported organisations and Chief Investigator organisation rules: ${title}`, async ({
      page,
    }) => {
      await fillBaseline(page, values);
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual(errors);
      await expect(page.locator(`#${panel} .has-error`)).toHaveCount(1);
    });
  }

  test('V7 Supported organisations and Chief Investigator organisation rules: disabled CI organisation', async ({
    page,
  }) => {
    test.fixme(
      true,
      'No disabled organisation is known on dashboard-s, and the ' +
        'organisations REST API cannot filter on enabled to find one.',
    );
    const DISABLED_ORG_ID = 'unknown';
    await fillBaseline(page, { 'investigators-0-primary_organisation': DISABLED_ORG_ID });
    await submitExpectingErrors(page);
    expect(await errorMap(page)).toEqual({
      'investigators-0-primary_organisation': [
        'This organisation is not (or no longer) valid: select an alternate one.',
      ],
    });
    await expect(page.locator('#panelFive .has-error')).toHaveCount(1);
  });

  // Grant cases: values and errors are for grants-0-<field>.  An empty
  // subtype for arc/nhmrc/mrff/rdc gets both the required error and the
  // family error.
  const grantCases: [string, Values, Errors][] = [
    [
      'ARC without subtype',
      { grant_type: 'arc', grant_subtype: '' },
      {
        grant_subtype: [REQUIRED, 'Select an ARC grant subtype for this grant'],
        grant_id: ['Enter the ARC grant id for this grant'],
      },
    ],
    [
      'NHMRC without subtype',
      { grant_type: 'nhmrc', grant_subtype: '' },
      {
        grant_subtype: [REQUIRED, 'Select an NHMRC grant subtype for this grant'],
        grant_id: ['Enter the NHMRC grant id for this grant'],
      },
    ],
    [
      'MRFF without subtype',
      { grant_type: 'mrff', grant_subtype: '' },
      {
        grant_subtype: [REQUIRED, 'Select an MRFF grant subtype for this grant'],
        grant_id: ['Enter the MRFF grant id for this grant'],
      },
    ],
    [
      'RDC without subtype, details or id',
      { grant_type: 'rdc', grant_subtype: '', funding_body_scheme: '', grant_id: '' },
      {
        grant_subtype: [REQUIRED, 'Select an RDC grant subtype for this grant'],
        funding_body_scheme: ['Provide details for this grant or a grant id (below!)'],
      },
    ],
    [
      'State with unspecified subtype',
      { grant_type: 'state', grant_subtype: 'unspecified' },
      { grant_subtype: ['Select the State for this grant'] },
    ],
    [
      'Institutional with a State subtype',
      { grant_type: 'inst', grant_subtype: 'nsw' },
      { grant_subtype: ['Inappropriate subtype for this grant'] },
    ],
    [
      'Institutional without details',
      { grant_type: 'inst', grant_subtype: 'unspecified', funding_body_scheme: '' },
      { funding_body_scheme: ['Provide details for this grant'] },
    ],
    // A non-blank subtype from the wrong family.
    [
      'ARC with an NHMRC subtype',
      { grant_type: 'arc', grant_subtype: 'nhmrc-ideas', grant_id: 'X1' },
      { grant_subtype: ['Select an ARC grant subtype for this grant'] },
    ],
    [
      'NHMRC with an ARC subtype',
      { grant_type: 'nhmrc', grant_subtype: 'arc-discovery', grant_id: 'X1' },
      { grant_subtype: ['Select an NHMRC grant subtype for this grant'] },
    ],
    [
      'MRFF with an RDC subtype',
      { grant_type: 'mrff', grant_subtype: 'rdc-wa', grant_id: 'X1' },
      { grant_subtype: ['Select an MRFF grant subtype for this grant'] },
    ],
    [
      'RDC with an ARC subtype',
      { grant_type: 'rdc', grant_subtype: 'arc-discovery', grant_id: 'X1' },
      { grant_subtype: ['Select an RDC grant subtype for this grant'] },
    ],
  ];
  const prefixed = <T>(o: Record<string, T>) =>
    Object.fromEntries(Object.entries(o).map(([k, v]) => [`grants-0-${k}`, v]));
  for (const [title, values, errors] of grantCases) {
    test(`V8 Grant rules: ${title}`, async ({ page }) => {
      await fillBaseline(page, prefixed(values));
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual(prefixed(errors));
      // All render in panel 7.
      await expect(page.locator('#panelSeven .has-error')).toHaveCount(
        Object.keys(errors).length,
      );
    });
  }

  const quotaCases: [string, string, string][] = [
    ['negative', '-1', 'Ensure this value is greater than or equal to 0.'],
    ['over 32 bits', '2147483648', 'Ensure this value is less than or equal to 2147483647.'],
  ];
  for (const [title, value, message] of quotaCases) {
    test(`V9 Quota bounds in the Custom Bundle modal: ${title}`, async ({ page }) => {
      await fillBaseline(page, { bundle: '', 'quota-compute.cores__nectar': value });
      await submitExpectingErrors(page);
      expect(await errorMap(page)).toEqual({ 'quota-compute.cores__nectar': [message] });
      // Step 2 is shown with the Custom card active, but the modal that
      // holds the error stays closed.
      await expect(page.locator('section#form-step2')).toBeVisible();
      await expect(page.locator('section#form-step1')).toBeHidden();
      await expect(page.locator('#modal-custom-bundle')).toBeHidden();
      await expect(page.locator('.bundle.active h4')).toHaveText('Custom');
      await expect(byId(page, 'id_bundle')).toHaveValue('');
      const group = page.locator('#modal-custom-bundle .has-error');
      await expect(group.locator('label')).toHaveText('Virtual Cores');
      await expect(group.locator('.help-block')).toHaveText(message);
      await expect(byId(page, 'id_quota-compute.cores__nectar')).toHaveValue(value);
    });
  }
});
