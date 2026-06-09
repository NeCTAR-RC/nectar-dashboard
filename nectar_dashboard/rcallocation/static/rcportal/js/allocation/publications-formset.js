/*
 * Publications formset ($.fn.pformset) and its field-visibility logic.
 *
 * A dynamic Django formset for research outputs / publications. Like the grants
 * formset it builds, deletes and renumbers rows client-side, but it also drives
 * a DOI-based workflow per row:
 *
 *   - create_row() builds the output-type select, the "have a DOI / no DOI"
 *     prompts, the DOI field with its "Validate DOI" button, and the manual
 *     citation textarea.
 *   - check_doi() looks a DOI up against the Crossref API and populates the
 *     DOI-checker modal (see doi-checker.js for the modal/result handling).
 *   - init_pub_form_visibility() / apply_pub_handlers() show or hide the DOI,
 *     prompts, citation and Crossref-details sections according to the chosen
 *     output type and whether a DOI / Crossref metadata is present.
 *
 * Depends on: utils.js (escapeText, apply_popover) and the render and format_*
 * helpers in doi-checker.js (used by check_doi at call time).
 */

// Publications formset
(function($) {

    function create_form_row(formset, opts) {
        var total_rows = $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').length;
        var form_new_row = create_row(opts.prefix, total_rows, opts);
        $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first').append(form_new_row);
        var new_row_id = 'id_' + opts.prefix + '-' + total_rows + '-id';
        var new_row_tr = $('input[id=' + new_row_id + ']').closest('fieldset');
        apply_pub_handlers(new_row_tr);
        init_pub_form_visibility(new_row_tr, '', true);
        total_rows += 1;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
    };

    function create_row(prefix, row_index, opts){
        var new_row = "<fieldset>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-id' id='id_" + opts.prefix + "-" + row_index + "-id'>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-DELETE' id='id_" + opts.prefix + "-" + row_index + "-DELETE'>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-crossref_metadata' id='id_" + opts.prefix + "-" + row_index + "-crossref_metadata'>";
        new_row += "<div class='publication_div'>";
        //output_type
        new_row += "<div class='form-group'>";
        new_row += create_field_div(opts, 'output_type', row_index, '');
        new_row += create_input_field_label(opts, 'output_type', 'Research Output type', row_index, false, "Select a publication type that best describes the publication. The 'Media publication' type is intended to encompass traditional media and 'new' media such as websites, blogs and social media.");
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_select_field(opts, 'output_type', row_index,
            [["", "Select a research output type"],
             ["AJ", "Peer reviewed journal article"],
             ["AP", "Other peer reviewed paper"],
             ["AN", "Non-peer reviewed paper"],
             ["B", "Book or book chapter"],
             ["M", "Media publication"],
             ["D", "Dataset"],
             ["S", "Software"],
             ["P", "Patent"],
             ["O", "Other"]]);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //doi prompts
        new_row += "<div class='prompts-group'>";
        new_row += "<p>";
        new_row += "All recently published books, articles and papers should ";
        new_row += "have a Digital Object Identifier (DOI) issued by the ";
        new_row += "publisher.  You will need to locate and provide that ";
        new_row += "DOI, if it exists.<br>Note that valid DOIs are ";
        new_row += "mandatory for peer reviewed journal articles.<br>";
        new_row += "If you do not have the DOI to hand, you can use ";
        new_row += "<a href='https://search.crossref.org/' target='_blank'>Crossref Metadata Search</a> ";
        new_row += "to try to find it. If no valid DOI exists, you will ";
        new_row += "need to enter the publication's citation details by hand.";
        new_row += "</p>";
        new_row += "<button type='button' name='have-doi' class='btn btn-default btn-sm'>";
        new_row += "I have a DOI to enter";
        new_row += "</button>&nbsp;";
        new_row += "<button type='button' name='no-doi' class='btn btn-default btn-sm'>";
        new_row += "This publication has no DOI";
        new_row += "</button>&nbsp;";
        new_row += "</div>";
        //doi
        new_row += create_field_div(opts, 'doi', row_index, 'hidden');
        new_row += create_input_field_label(opts, 'doi', 'Digital Object Identifier(DOI)', row_index, false, "Provide the Research Output's DOI. A DOI should be provided for all books and peer-reviewed papers. A valid DOI starts with '10.&lt;number&gt;/'. This is followed by letters, numbers and other characters. For example: '10.23456/abc-123'.");
        new_row += "<div class='controls'>";
        new_row += "<div class='form-inline'>";
        new_row += "<div class='form-group'>";
        new_row += create_input_field(opts, 'doi', 'text', 'maxlength="256"', row_index);
        new_row += "&nbsp;<button type='button' id='check-doi' class='btn btn-default'>";
        new_row += "Validate DOI";
        new_row += "</button>";
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        new_row += "<p class='mt-3'><a href='https://search.crossref.org/' target='_blank'>Search for my DOI</a> on crossref.org.</p>";
        new_row += "</div>";
        //publication
        new_row += create_field_div(opts, 'publication', row_index, 'hidden');
        new_row += create_input_field_label(opts, 'publication', 'Citation reference', row_index, false, "Provide details of the Research Output according to its type. For example a Paper or Book's citation, a Dataset's title and URI, Software product's name and website URL, a Patent's title and number. This field should not be used for Research Outputs with DOIs known to CrossRef.");
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_textarea_field(opts, 'publication',
                                         'maxlength="512"',
                                         row_index);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        // details
        new_row += "<div id='details-group'>";
        new_row += "<label>Crossref Details</label>";
        new_row += "<div id='details-text'>";
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        // closed details div
        new_row += "<button type='button' id='delete-publication' class='btn btn-danger field-delete-btn'>";
        new_row += "<i class='fa fa-close'></i> Delete";
        new_row += "</button>";
        new_row += "</fieldset>";
        return new_row;
    };

    function create_select_field(opts, field_name, row_index, options){
        var select = "<select name='"+ opts.prefix + "-" + row_index + "-" + field_name + "' id='id_" + opts.prefix + "-" + row_index + "-" + field_name +"' class='form-control'>";
        for (var i = 0; i < options.length; i++) {
            select += "<option value='" + options[i][0] + "'";
            if (options[i].length > 2) {
                select += " " + options[i][2];
            }
            select += ">" + options[i][1] + "</option>";
        }
        select += "</select>";
        return select;
    };

    function create_field_div(opts, field_name, row_index, extra) {
        return "<div class='form-group' id='id_" +
            opts.prefix + "-" + row_index + "-" + field_name + "-group' " +
            extra + ">";
    };

    function create_input_field_label(opts, field_name, field_label, row_index, required, help_text){
        label_section = "<label for='id_"+ opts.prefix + "-" + row_index + "-" + field_name +"'>";
        label_section += field_label;
        if(required == true){
            label_section += "<span class='glyphicon glyphicon-asterisk text-primary'></span>";
        }
        if (help_text) {
            label_section += "<img class='help-popover' src='/static/rcportal/img/help.png' data-content='" + escapeText(help_text) + "' data-original-title='" + field_label + "' data-html='true'>";
        }
        label_section += "</label>";
        return label_section;
    };

    function create_help_span(opts, field_name, row_index, help_txt){
        var help_span = "<span class='help-block'>";
        help_span += "<div class='help-text-div' id='id_" + opts.prefix + "-" + row_index +"-" + field_name + "'>";
        help_span += escapeText(help_text);
        help_span += "</div>";
        help_span += "</span>";
        return help_span;
    };

    function create_input_field(opts, field_name, type, extra, row_index){
        return "<input type='" + type + "' name='" + opts.prefix + "-" + row_index + "-" + field_name + "' id='id_" + opts.prefix + "-" + row_index + "-" + field_name + "' " + extra + " class='form-control'>";
    };

    function create_textarea_field(opts, field_name, extra, row_index){
        return "<textarea name='" + opts.prefix + "-" + row_index + "-" + field_name + "' id='id_" + opts.prefix + "-" + row_index + "-" + field_name + "' " + extra + " class='form-control'></textarea>";
    };

    function delete_form_row(formset, opts, span){
        var current_tr = span.closest('fieldset');
        //check the input id field is empty or not
        var id_input = current_tr.find('input[id$=-id]');

        var id_value = id_input.val();
        if (id_value == null || id_value == ''){
            //just remove the current row as it's a new row.
            // and resort the whole table rows
            current_tr.remove();
            resort_form_rows(formset, opts);
        } else{
            //check the input delete field
            var del_input_field = current_tr.find('input[id$=-DELETE]');
            //set the delete flag to true
            del_input_field.val('True');
            current_tr.toggleClass('hidden');
        }
        //reset the total_forms_input value
        var total_rows = $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').length;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
    };

    function check_doi(span){
        var current_tr = span.closest('fieldset');
        var doi_input = current_tr.find('input[id$=-doi]');
        var doi = doi_input.val();
        if (! doi) {
            // Treat this as a miss-click
            return;
        }
        if (! doi.match(/^10\.[0-9]+\//)) {
            // DOI is not in standard format
            var match = doi.match(/^https?:[a-z0-9./_\\]+?\/(10\..+)$/i);
            if (!match) {
                match = doi.match(/^doi:\/*(10\..+)$/i);
            }
            if (match) {
                // Fix it if we can
                doi = match[1];
                doi_input.val(doi);
                alert("Converted the DOI to the required format: " + doi);
            } else {
                // There is no point validating this DOI ...
                alert("This DOI is not recogizable: please refer to the help text");
                return;
            }
        }
        var row_no = doi_input.attr('id').match(/.*-([0-9]+)-doi$/)[1];
        $('#doi-row').val(row_no);
        $('#doi-doi').val(doi);
        $('#doi-checker-state').val('checking');
        $('#doi-title').val('');
        $('#doi-publication').val('');
        $('#doi-authors').val('');
        $('#doi-year').val('')
        $('#doi-crossref').val('');
        $('#modal-doi-checker').modal('show');
        $.ajax({
            url: "https://api.crossref.org/works/" + doi,
            dataType: "text"    // we need to parse the JSON ourselves
        }).done(function(jsonString, text, jqxhr) {
            var data = JSON.parse(jsonString);
            $('#modal-doi-checker').modal('toggle');
            $('#doi-checker-state').val('found');
            var msg = data.message;
            $('#doi-title').val(format_title(msg));
            $('#doi-publication').val(format_publication(msg));
            $('#doi-authors').val(format_authors(msg));
            $('#doi-year').val(format_pub_date(msg));
            $('#doi-crossref').val(jsonString);
            $('#modal-doi-checker').modal('toggle');
        }).fail(function(jqxhr, text, errorThrown) {
            $('#modal-doi-checker').modal('toggle');
            if (jqxhr.status == 404) {
                $('#doi-checker-state').val('not-found');
            } else {
                $('#doi-checker-state').val('failed');
            }
            $('#modal-doi-checker').modal('toggle');
        });
    };

    function resort_form_rows(formset, opts){
        var match = new RegExp(opts.prefix + '-\\d+-', 'g');

        $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').each(function(index) {
            //reindex the id input field
            var id_input = $(this).find('input[id$=-id]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + index + '-id');
            id_input.attr('name', opts.prefix + '-' + index + '-id');

            //reindex the delete input field
            var id_input = $(this).find('input[id$=-DELETE]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + index + '-DELETE');
            id_input.attr('name', opts.prefix + '-' + index + '-DELETE');

            //reindex the crossref input field
            var id_input = $(this).find('input[id$=-crossref_metadata]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + index + '-crossref_metadata');
            id_input.attr('name', opts.prefix + '-' + index + '-crossref_metadata');

            //reindex the label fors
            $(this).find("label[for^='id_" + opts.prefix + "-']").each(function(){
                var labelFor = $(this).attr('for').replace(match, opts.prefix +'-' + index + '-');
                $(this).attr('for', labelFor);
            });

            //reindex the divs
            $(this).find("div[id^='id_" + opts.prefix + "-']").each(function(){
                var divId = $(this).attr('id').replace(match, opts.prefix +'-' + index + '-');
                $(this).attr('id', divId);
            });

            //reindex select id and name
            $(this).find("select.form-control").each(function(){
                var selectId = $(this).attr('id').replace(match, opts.prefix + '-' + index + '-');
                var selectName = $(this).attr('name').replace(match, opts.prefix + '-' + index + '-');
                $(this).attr('id', selectId);
                $(this).attr('name', selectName);
            });

            //reindex textarea id and name
            $(this).find("textarea.form-control").each(function(){
                var textId = $(this).attr('id').replace(match, opts.prefix + '-' + index + '-');
                var textName = $(this).attr('name').replace(match, opts.prefix + '-' + index + '-');
                $(this).attr('id', textId);
                $(this).attr('name', textName);
            });

            //reindex the input id and name
            $(this).find("input.form-control").each(function(){
                var inputId = $(this).attr('id').replace(match, opts.prefix + '-' + index + '-');
                var inputName = $(this).attr('name').replace(match, opts.prefix + '-' + index + '-');
                $(this).attr('id', inputId);
                $(this).attr('name', inputName);
            });
        });
    };

    $.fn.pformset = function(options) {
        var opts = $.extend( {}, $.fn.pformset.defaults, options );
         return this.each(function() {
             //set current formset
             var formset = this;
             $('div.' + options.formset_class_id).on('click', '#add_another', function (event) {
                 event.preventDefault();
                 create_form_row(formset, opts);
                 apply_popover();
             });
             $('div.' + options.formset_class_id).on('click', '#delete-publication', function (event){
                 event.preventDefault();
                 var clicked_span = $(this);
                 delete_form_row(formset, opts, clicked_span);
             });
             $('div.' + options.formset_class_id).on('click', '#check-doi', function (event){
                 event.preventDefault();
                 var clicked_span = $(this);
                 check_doi(clicked_span);
             });
             $('div.' + options.formset_class_id + ' div.more_fields_tab > div:first fieldset').each(function (){
                 var tr = $(this);
                 var output_group = tr.find('div[id*=-output_type-group]');
                 if (!output_group.attr('hidden')) {
                     apply_pub_handlers(tr);
                     init_pub_form_visibility(tr, false);
                 }
             });
         });
    };

    $.fn.pformset.defaults = {
        form_prefix: "",
        formset_class_id: ""
    };

}(jQuery));

function init_pub_form_visibility(tr, type_changed) {
    var prompts_group = tr.find('div[class=prompts-group]');
    var doi_group = tr.find('div[id*=-doi-group]');
    var doi_input = tr.find('input[id*=-doi]');
    var details_group = tr.find('div[id=details-group]');
    var meta_input = tr.find('input[id*=-crossref_metadata]');
    var pub_group = tr.find('div[id*=-publication-group]');
    var pub_input = tr.find('input[id*=-publication]');
    var output_type = tr.find('select[id*=-output_type]').val();

    if (output_type == 'AJ' || output_type == 'AP' ||
        output_type == 'AN' || output_type == 'B') {
        if (!doi_input.val() && output_type != 'AJ') {
            doi_group.hide();
            prompts_group.show();
            details_group.hide();
        } else {
            doi_group.show();
            prompts_group.hide();
            if (meta_input.val()) {
                details_group.show();
            } else {
                details_group.hide();
            }
        }
        if (type_changed) {
            pub_input.val('');
            pub_group.hide();
        } else if (meta_input.val() || output_type == 'AJ') {
            pub_group.hide();
        } else {
            pub_group.show();
        }
    } else {
        doi_input.val('');
        meta_input.val('');
        doi_group.hide();
        prompts_group.hide();
        details_group.hide();
        if (output_type) {
            pub_group.show();
        } else {
            pub_group.hide();
        }
    }
}

function apply_pub_handlers(tr) {
    tr.off('change', 'select[id*=-output_type]');
    tr.on('change', 'select[id*=-output_type]', function(e) {
        init_pub_form_visibility(tr, true);
    });
    tr.off('change', 'input[name*=-doi]');
    tr.on('change', 'input[name*=-doi]', function(e) {
        $(this).val($.trim($(this).val())); // Trim whitespace from start and end
        tr.find('input[id*=-crossref_metadata]').val('');
        tr.find('div[id=details-group]').hide();
    });
    tr.off('click', 'button[name=have-doi]');
    tr.on('click', 'button[name=have-doi]', function(e) {
        var current_tr = tr;
        current_tr.find('div[class=prompts-group]').hide();
        current_tr.find('div[id*=-doi-group]').show();
        current_tr.find('div[id=details-group]').hide()
        current_tr.find('div[id*=-publication-group]').hide();
    });
    tr.off('click', 'button[name=no-doi]');
    tr.on('click', 'button[name=no-doi]', function(e) {
        var current_tr = tr;
        var output_type = current_tr.find('select[id*=-output_type]');
        if (output_type.val() == "AJ") {
            output_type.val("");
            init_pub_form_visibility(current_tr, true);
        } else {
            current_tr.find('div[class=prompts-group]').hide();
            current_tr.find('div[id*=-doi-group]').hide();
            current_tr.find('div[id=details-group]').hide()
            current_tr.find('div[id*=-publication-group]').show();
        }
    });
}
