/*
 * DOI checker modal and Crossref metadata handling.
 *
 * Drives the #modal-doi-checker dialog that appears when a user validates a
 * publication DOI (the lookup itself lives in publications-formset.js):
 *
 *   - The 'shown.bs.modal' handler shows the right modal content for the
 *     current state (checking / found / not-found / failed).
 *   - format_author/format_authors/format_pub_date/format_title/
 *     format_publication turn a Crossref message object into display strings.
 *   - render_crossref_metadata() renders stored Crossref JSON for a row.
 *   - accept_doi()/reject_doi() store or clear the Crossref metadata on the
 *     publication row when the user accepts or rejects the looked-up details.
 *
 * Depends on: utils.js (escapeText) and publications-formset.js
 * (init_pub_form_visibility).
 */

$('#modal-doi-checker').on('shown.bs.modal', function (e) {
    var state = $('#doi-checker-state').val();
    if (state == 'checking') {
        $('#doi-checking').show();
    } else {
        $('#doi-checking').hide();
    }
    if (state == 'found') {
        $('#doi-found').show();
        $('#doi-question').show();
        $('#doi-accept').show();
        $('#doi-reject').show();
        $('#doi-close').hide();
    } else {
        $('#doi-found').hide();
        $('#doi-question').hide();
        $('#doi-accept').hide();
        $('#doi-reject').hide();
        $('#doi-close').show();
    }
    if (state == 'not-found') {
        $('#doi-not-found').show();
    } else {
        $('#doi-not-found').hide();
    }
    if (state == 'failed') {
        $('#doi-failed').show();
    } else {
        $('#doi-failed').hide();
    }
});

function format_author(author) {
    if (author.family) {
        if (author.given) {
            return author.family + "," + author.given;
        } else {
            return author.family;
        }
    } else if (author.given) {
        return author.given;
    } else if (author.name) {
        return author.name;
    } else {
        return "no name";
    }
};

function format_authors(msg) {
    var authors = msg['author'];
    var text = "Not recorded";
    if (authors) {
        text = authors.slice(0, 5)
                      .map(author => format_author(author)).join(";");
        if (authors.length > 5) {
            text = text + " ...";
        }
    }
    return escapeText(text)
};

function format_pub_date(msg) {
    var pub_date = msg['published-print'] || msg['published-online'];
    return escapeText(pub_date ? pub_date['date-parts'][0][0]
                      : "Not recorded");
};

function format_title(msg) {
    return escapeText(msg['title'] || "Not recorded");
};

function format_publication(msg) {
    return escapeText(msg['container-title'] || "Not recorded");
};

function render_crossref_metadata(json) {
    try {
        var data = JSON.parse(json);
        if (Array.isArray(data)) {
            return "*** Not a JSON object ***";
        }
        if (!data.hasOwnProperty('message')) {
            return "*** Not a Crossref response object ***";
        }
        var msg = data.message;
        return "<i>Title</i>: " + format_title(msg) +
            ", <i>Author(s)</i>: " + format_authors(msg) +
            ", <i>Publication</i>: " + format_publication(msg) +
            ", <i>Year</i>: " + format_pub_date(msg);
    } catch (ex) {
        return "*** Invalid JSON ***";
    }
};

function accept_doi(e) {
    e.preventDefault();
    var row_no = $('#doi-row').val();
    var crossref_input = $('#id_publications-' + row_no + '-crossref_metadata');
    var tr = crossref_input.closest('fieldset');
    var details = tr.find('div[id=details-text]');
    var metadata = $('#doi-crossref').val();
    crossref_input.val(metadata);
    details.html(render_crossref_metadata(metadata));
    init_pub_form_visibility(tr, false)
};

function reject_doi(e) {
    e.preventDefault();
    var row_no = $('#doi-row').val();
    var doi = $('#doi-doi').val();
    var crossref_input = $('#id_publications-' + row_no + '-crossref_metadata');
    var tr = crossref_input.closest('fieldset');
    var details = tr.find('div[id=details-text]');
    crossref_input.val('');
    details.html("No information available for DOI " + doi);
    init_pub_form_visibility(tr, false)
};

$('.doi-close').click(reject_doi);
$('#doi-reject').click(reject_doi);
$('#doi-accept').click(accept_doi);
