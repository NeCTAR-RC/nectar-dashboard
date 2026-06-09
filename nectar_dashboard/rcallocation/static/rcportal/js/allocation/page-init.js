/*
 * Page initialisation and form submit helper.
 *
 *   - On DOM ready: initialise the date pickers, the help popovers and the
 *     DNS service-name field.
 *   - submit_ignore(): submit the allocation form with the hidden
 *     "ignore warnings" flag set, so the server skips the quota-sanity and
 *     other advisory warning checks.
 *
 * Depends on: utils.js (apply_popover) and dns-service-name.js
 * (populate_dns_service_name).
 */

$(function() {
    //date picker
    $(".datepicker2").datepicker({
        autoclose: true,
        changeMonth: true,
        changeYear: true,
        format: 'yyyy-mm-dd',
        todayHighlight: true,
    });

    apply_popover();

    populate_dns_service_name();
});

var submit_ignore_in_progress = false;

function submit_ignore() {
    // Submit the allocation form with the hidden field set to tell the
    // server side to not to check for quota sanity and other warnings.
    // The in-progress flag stops a double-click sending the form twice
    // (this path bypasses horizon.forms.handle_submit's guard because
    // it submits natively rather than via a submit event).
    if (submit_ignore_in_progress) { return; }
    submit_ignore_in_progress = true;
    document.getElementById("id_ignore_warnings").value = '1';
    document.querySelectorAll('.submit-form-button').forEach(function(b) {
        b.disabled = true;
    });
    document.getElementById("new-allocation").submit();   // sic
}
