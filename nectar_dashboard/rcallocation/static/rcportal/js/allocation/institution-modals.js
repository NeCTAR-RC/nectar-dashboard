/*
 * Institution-specific welcome modals.
 *
 * On first load of a new allocation request form, show an institution-specific
 * information modal when the contact email matches a known pattern:
 *
 *   - University of Melbourne (#modal-uom-dashboard)
 *   - Western Australian universities served by Pawsey (#modal-pawsey)
 *
 * isNewAllocationRequest() is defined in the page template.
 */

// Show UoM modal on first load of a new allocation request form if
// the contact email matches the hard-wired UoM email pattern.
$(function(){
  if ($('#id_contact_email').length) {
    var email = $('#id_contact_email').val();
    var show = email.match(/^.+@(.+\.)*unimelb\.edu\.au$/);
    if (show != null && isNewAllocationRequest() /* see template */ ) {
      $('#modal-uom-dashboard').modal('show');
    }
  }
});

// Show Pawsey modal on first load of a new allocation request form if
// the contact email matches any of W.A Universities' email pattern.
$(function(){
  if ($('#id_contact_email').length) {
    var email = $('#id_contact_email').val();
    var show = email.match(/^.+@(.+\.)*uwa\.edu\.au$|^.+@(.+\.)*murdoch\.edu\.au$|^.+@curtin\.edu\.au$|^.+@nd\.edu\.au$|^.+@ecu\.edu\.au$/);
    if (show != null && isNewAllocationRequest() /* see template */ ) {
      $('#modal-pawsey').modal('show');
    }
  }
});
