/*
 * Propose-a-new-organisation handler.
 *
 * Posts the "propose organisation" form to /rest_api/organisations/ so a user
 * can register an organisation that isn't yet in the ROR-backed list. Shows a
 * provisional-acceptance message on success, or per-field validation errors
 * (HTTP 400) / a generic error otherwise. A module-level flag guards against
 * double submission while a request is in flight.
 */

var propose_in_progress = false;

function propose_organisation(e) {
    e.preventDefault();
    if (propose_in_progress) {
        return;
    }

    function set_error(name, value) {
        $('#id-prop-' + name + '-err').html(value);
    }

    var form = $('#propose-form');
    $('#propose-message').html('');
    ['full_name', 'short_name', 'country', 'url'].forEach(
        function(c) { set_error(c, ''); });

    $.ajax({
        url: "/rest_api/organisations/",
        method: "POST",
        data: {
            full_name: form.find('input[name=full-name]').val(),
            short_name: form.find('input[name=short-name]').val(),
            country: form.find('select[name=country] option:selected').val(),
            url: form.find('input[name=url]').val()
        },
        xhrFields: {
            withCredentials: true
        },
        beforeSend : function(jxqr, settings) {
            propose_in_progress = true;
        }
    }).done(function(jsonString, text, jqxhr) {
        propose_in_progress = false;
        $('#propose-message').html(
            "Organisation provisionally accepted.  You can now use it in " +
                "your Allocation Requests pending vetting.");
        $('#propose-message').removeClass("alert alert-danger");
        $('#propose-message').addClass("alert alert-warning");

    }).fail(function(jqxhr, text, errorThrown) {
        propose_in_progress = false;
        var response_data = $.parseJSON(jqxhr.responseText)
        if (jqxhr.status == 400) {
            for (var key in response_data) {
                set_error(key, response_data[key].join('; '));
            }
            $('#propose-message').html('Organisation not accepted.');
            $('#propose-message').removeClass("alert alert-warning");
            $('#propose-message').addClass("alert alert-danger");
        } else {
            $('#propose-message').html('Something went wrong');
            $('#propose-message').removeClass("alert alert-warning");
            $('#propose-message').addClass("alert alert-danger");
        }
    });
};

$('#propose-organisation').click(propose_organisation);
