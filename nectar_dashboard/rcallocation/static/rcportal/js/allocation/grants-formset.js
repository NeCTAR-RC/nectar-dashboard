/*
 * Grants formset ($.fn.gformset).
 *
 * A dynamic Django formset for research grants. Lets the user add/delete grant
 * rows on the client, building each row's markup (grant type/subtype selects,
 * funding details, year and amount inputs) and renumbering form indices so the
 * formset's management-form counts stay consistent on submit.
 *
 * fix_grant_subtype_options() filters the subtype dropdown to the options valid
 * for the chosen grant type.
 *
 * Depends on: utils.js (escapeText, apply_popover).
 */

// Grants formset
(function($) {
    var this_year = new Date().getFullYear().toString();
    var next_year = (new Date().getFullYear() + 1).toString();

    function create_form_row(formset, opts) {
        var total_rows = $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').length;
        var form_new_row = create_row(opts.prefix, total_rows, opts);
        $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first').append(form_new_row);
        fix_grant_subtype_options($('#id_' + opts.prefix + '-' + total_rows + '-' + 'grant_subtype'), true);
        total_rows += 1;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
    };

    function create_row(prefix, row_index, opts){
        var new_row = "<fieldset>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-id' id='id_" + opts.prefix + "-" + row_index + "-id'>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-DELETE' id='id_" + opts.prefix + "-" + row_index + "-DELETE'>";
        new_row += "<div class='grant_div'>";
        //type
        new_row += "<div class='form-group'>";
        new_row += create_input_field_label(opts, 'grant_type', 'Grant Type', row_index, true, 'Choose the grant type from the dropdown options.');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_select_field(opts, 'grant_type', row_index,
            [["", "---------"],
             ["arc", "Australian Research Council"],
             ["nhmrc", "NHMRC"],
             ["mrff", "Medical Research Future Fund (MRFF)"],
             ["rdc", "Rural Research and Development Corporations (RDCs)"],
             ["comp", "Other Australian Federal Govt competitive grant"],
             ["govt", "Australian Federal Govt non-competitive funding"],
             ["state", "Australian State / Territory Govt funding"],
             ["industry", "Industry funding"],
             ["ext", "Other external funding"],
             ["inst", "Institutional research funding"],
             ["nz", "New Zealand research funding"]]);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //subtype
        new_row += "<div class='form-group '>";
        new_row += create_input_field_label(opts, 'grant_subtype', 'Grant Subtype', row_index, true, 'Choose an applicable grant subtype from the dropdown options.  If no option is applicable, choose "unspecified" and then fill in the "Other funding source details" field below.');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_select_field(opts, 'grant_subtype', row_index,
            [["", "---------"],
             ["arc-discovery", "ARC Discovery project"],
             ["arc-indigenous", "ARC Discovery Indigenous"],
             ["arc-decra", "ARC Discovery Early Career Researcher Award"],
             ["arc-future", "ARC Future Fellowship"],
             ["arc-laureate", "ARC Laureate Fellowship"],
             ["arc-itrp", "ARC Industry Transformation Research Program"],
             ["arc-linkage", "ARC Linkage Project"],
             ["arc-coe", "ARC Centre of Excellence"],
             ["arc-lief", "ARC Linkage Infrastructure Equipment and Facilities"],
             ["arc-sri", "ARC Special Research Initiative"],
             ["arc-llasp", "ARC Linkage Learned Academies Special Project"],
             ["arc-other", "Other ARC grant"],
             ["nhmrc-investigator", "NHMRC Investigator grant"],
             ["nhmrc-synergy", "NHMRC Synergy grant"],
             ["nhmrc-ideas", "NHMRC Ideas grant"],
             ["nhmrc-strategic", "NHMRC Strategic or Leverage grant"],
             ["nhmrc-program", "NHMRC Program grant"],
             ["nhmrc-project", "NHMRC Project grant"],
             ["nhmrc-fas", "NHMRC Fellowship or Scholarship (various)"],
             ["nhmrc-core", "NHMRC Center of Research Excellence"],
             ["nhmrc-development", "NHMRC Development grant"],
             ["nhmrc-equipment", "NHMRC Equipment grant"],
             ["nhmrc-ctcs", "NHMRC Clinical Trial and Cohort Studies grant"],
             ["nhmrc-ics", "NHMRC International Collaborations (various)"],
             ["nhmrc-pc", "NHMRC Partnership Centre"],
             ["nhmrc-pp", "NHMRC Partnership project"],
             ["nhmrc-tcr", "NHMRC Targeted Calls for Research"],
             ["nhmrc-iriiss", "NHMRC Independent Research Institute Infrastructure Support Scheme"],
             ["nhmrc-bdri", "NHMRC Boosting Dementia Research Initiatives (various)"],
             ["nhmrc-other", "Other NHMRC scheme"],
             ["mrff-brain-cancer", "MRFF Australian Brain Cancer Mission"],
             ["mrff-cardiovascular", "MRFF Cardiovascular Health Mission"],
             ["mrff-clinical-trials", "MRFF Clinical Trials Activity"],
             ["mrff-clinician-researchers", "MRFF Clinician Researchers"],
             ["mrff-coronavirus", "MRFF Coronavirus Research Response"],
             ["mrff-dementia-ageing", "MRFF Dementia, Ageing and Aged Care Mission"],
             ["mrff-emcr", "MRFF Early to Mid-Career Researchers"],
             ["mrff-epcdr", "MRFF Emerging Priorities and Consumer Driven Research"],
             ["mrff-frontier", "MRFF Frontier Health and Medical Research"],
             ["mrff-genomics", "MRFF Genomics Health Futures Mission"],
             ["mrff-global-health", "MRFF Global Health"],
             ["mrff-indigenous", "MRFF Indigenous Health Research Fund"],
             ["mrff-commercialisation", "MRFF Medical Research Commercialisation"],
             ["mrff-million-minds", "MRFF Million Minds Mental Health Research Mission"],
             ["mrff-ncri", "MRFF National Critical Research Infrastructure"],
             ["mrff-preventive", "MRFF Preventive and Public Health Research"],
             ["mrff-primary-care", "MRFF Primary Health Care Research"],
             ["mrff-rart", "MRFF Rapid Applied Research Translation"],
             ["mrff-rdi", "MRFF Research Data Infrastructure"],
             ["mrff-redi", "MRFF Researcher Exchange and Development Within Industry"],
             ["mrff-stem-cell", "MRFF Stem Cell Therapies Mission"],
             ["mrff-tbi", "MRFF Traumatic Brain Injury Mission"],
             ["mrff-other", "Other MRFF initiative"],
             ["rdc-wa", "Wine Australia"],
             ["rdc-crdc", "Cotton RDC"],
             ["rdc-frdc", "Fisheries RDC"],
             ["rdc-grdc", "Grains RDC"],
             ["rdc-agrifutures", "Rural Industries RDC (AgriFutures Australia)"],
             ["rdc-ael", "Australian Eggs Ltd"],
             ["rdc-livecorp", "Australian Livestock Export Corp Ltd (LiveCorp)"],
             ["rdc-ampc", "Australian Meat Processor Corp"],
             ["rdc-apl", "Australian Pork Ltd"],
             ["rdc-awil", "Australian Wool Innovation Ltd"],
             ["rdc-dal", "Dairy Australia Ltd"],
             ["rdc-fwpa", "Forest and Wood Products Australia"],
             ["rdc-hial", "Horticulture Innovation Australia Ltd"],
             ["rdc-mla", "Meat and Livestock Australia"],
             ["rdc-sral", "Sugar Research Australia Ltd"],
             ["act", "Australian Capital Territory Govt funding"],
             ["nsw", "New South Wales Govt funding"],
             ["nt", "Northern Territory Govt funding"],
             ["qld", "Queensland Govt funding"],
             ["sa", "South Australia Govt funding"],
             ["tas", "Tasmania Govt funding"],
             ["vic", "Victoria Govt funding"],
             ["wa", "Western Australia Govt funding"],
             ["unspecified", "unspecified"]]);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //funding body_scheme
        new_row += "<div class='form-group '>";
        new_row += create_input_field_label(opts, 'funding_body_scheme', 'Other funding source details', row_index, false, 'For example, details of a state government grant scheme, or an industry funding source.');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_input_field(opts, 'funding_body_scheme', 'Funding body and scheme', row_index, 255);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //grant id
        new_row += "<div class='form-group '>";
        new_row += create_input_field_label(opts, 'grant_id', 'Grant ID', row_index, false, 'Specify the grant id.');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_input_field(opts, 'grant_id', 'Grant ID', row_index);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //first_year_funded
        new_row += "<div class='form-group '>";
        new_row += create_input_field_label(opts, 'first_year_funded', 'First year funded', row_index, true, 'Specify the first year funded');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_year_input_field(opts, 'first_year_funded', this_year, row_index);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //last_year_funded
        new_row += "<div class='form-group '>";
        new_row += create_input_field_label(opts, 'last_year_funded', 'Last year funded', row_index, true, 'Specify the last year funded');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_year_input_field(opts, 'last_year_funded', next_year, row_index);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        //total funding
        new_row += "<div class='form-group '>";
        new_row += create_input_field_label(opts, 'total_funding', 'Total funding (AUD)', row_index, true, 'Total funding amount in AUD.');
        new_row += "<div class='controls'>";
        new_row += "<div class='input-g'>";
        new_row += create_number_input_field(opts, 'total_funding', '0', row_index);
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
        // closed grant_div
        new_row += "<button type='button' id='delete-grant' class='btn btn-danger field-delete-btn'>";
        new_row += "<i class='fa fa-close'></i> Delete";
        new_row += "</button>";
        new_row += "</fieldset>";
        return new_row;
    };

    function create_input_field_label(opts, field_name, field_label, row_index, required, help_text){
        label_section = "<label for='id_"+ opts.prefix + "-" + row_index + "-" + field_name +"'>";
        label_section += field_label;
        if(required == true){
            label_section += "<span class='glyphicon glyphicon-asterisk text-primary'></span>";
        }
        label_section += "<img class='help-popover' src='/static/rcportal/img/help.png' data-content='" + escapeText(help_text) + "' data-original-title='" + field_label + "' data-html='true'>";
        label_section += "</label>";
        return label_section;
    };

    function create_select_field(opts, field_name, row_index, options){
        var select = "<select name='"+ opts.prefix + "-" + row_index + "-" + field_name + "' id='id_" + opts.prefix + "-" + row_index + "-" + field_name +"' class='form-control'>";
        for (var i = 0; i < options.length; i++) {
            select += "<option value='" + options[i][0] + "'>" + options[i][1] + "</option>";
        }
        select += "</select>";
        return select;
    };

    function create_help_span(opts, field_name, row_index, help_txt){
        var help_span = "<span class='help-block'>";
        help_span += "<div class='help-text-div' id='id_" + opts.prefix + "-" + row_index +"-" + field_name + "'>";
        help_span += escapeText(help_txt);
        help_span += "</div>";
        help_span += "</span>";
        return help_span;
    };

    function create_input_field(opts, field_name, field_label, row_index, maxlength){
        maxlength = maxlength || 200;
        return "<input type='text' name='" + opts.prefix + "-" + row_index + "-" + field_name + "' maxlength='" + maxlength + "' id='id_" + opts.prefix + "-" + row_index + "-" + field_name + "' class='form-control'>";
    };

    function create_number_input_field(opts, field_name, default_value, row_index){
        return "<input type='number' name='" + opts.prefix + "-" + row_index + "-" + field_name
            + "' maxlength='200' id='id_" + opts.prefix + "-" + row_index + "-" + field_name
            + "' class='form-control' " + "value='" + default_value + "' min='0'>";
    };

    function create_year_input_field(opts, field_name, default_value, row_index){
       return "<input type='number' name='" + opts.prefix + "-" + row_index
           + "-" + field_name + "' value='" + default_value + "' id='id_" + opts.prefix + "-"
           + row_index + "-" + field_name + "' min='1970' max='3000' class='form-control'>"
    };

    function delete_form_row(formset, opts, span){
        var span_id = span.attr('id');
        var current_tr = span.closest('fieldset');
        //check the input id field is empty or not
        var id_input = current_tr.find('input[id$=-id]');

        var id_value = id_input.val();
        if (id_value == null || id_value == ''){
            //remove the current row as it's a new row.
            current_tr.remove();
            //renumber the remaining row's ids.
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

            //reindex the label fors
            $(this).find("label[for^='id_" + opts.prefix + "-']").each(function(){
                var labelFor = $(this).attr('for').replace(match, opts.prefix +'-' + index + '-');
                $(this).attr('for', labelFor);
            });

            //reindex select id and name
            $(this).find("select.form-control").each(function(){
                var selectId = $(this).attr('id').replace(match, opts.prefix + '-' + index + '-');
                var selectName = $(this).attr('name').replace(match, opts.prefix + '-' + index + '-');
                $(this).attr('id', selectId);
                $(this).attr('name', selectName);
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

    function set_default_dates(opts) {
        // Set default funding dates in the form for grants with no dates
        $('input[name$="first_year_funded"]').each(function(){
            if (!$(this).val()) {
                $(this).val(this_year);
            };
        });
        $('input[name$="last_year_funded"]').each(function(){
            if (!$(this).val()) {
                $(this).val(next_year);
            };
        });
    };

    function fix_grant_subtype_options(type_selector, reselect) {
        // Show / hide grant subtype options according to the selected
        // grant type.  If reselect it true, also reselect the subtype
        // if the current selection is invalid.
        var type = type_selector.val();
        var type_id = type_selector.attr('id');
        var subtype_id = type_id.replace(/grant_type/, 'grant_subtype');
        var pattern;
        var unspecified_only = false;
        var no_selection = false;
        if (type == 'arc') {
            pattern = /^arc-.*$/;
        } else if (type == 'nhmrc') {
            pattern = /^nhmrc-.*$/;
        } else if (type == 'mrff') {
            pattern = /^mrff-.*$/;
        } else if (type == 'rdc') {
            pattern = /^rdc-.*$/;
        } else if (type == 'state') {
            pattern = /^(act|nsw|nt|qld|sa|tas|vic|wa)$/;
        } else if (type == '') {
            pattern = /^$/;   // no selection allowed ...
            no_selection = true;
        } else {
            pattern = /^unspecified$/;
            unspecified_only = true;
        }
        $('#' + subtype_id + ' option').each(function() {
            if ($(this).val().match(pattern)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
        current = $('#' + subtype_id + ' option:selected');
        if (!current.val().match(pattern)) {
            if (unspecified_only) {
                current.prop("selected", false);
                $('#' + subtype_id + ' option[value="unspecified"]').prop("selected", true);
            }
            else if (reselect) {
                current.prop("selected", false);
            }
        }
        if (unspecified_only || no_selection) {
            $('#' + subtype_id).closest('div[class~="form-group"]').hide();
        } else {
            $('#' + subtype_id).closest('div[class~="form-group"]').show();
        }
    };

    $.fn.gformset = function(options) {
        var opts = $.extend( {}, $.fn.gformset.defaults, options );
        return this.each(function() {
            //set current formset
            var formset = this;
            var context = 'div.' + options.formset_class_id;
            $(context).on('click', '#add_another', function (event) {
                event.preventDefault();
                create_form_row(formset, opts);
                apply_popover();
            });
            $(context).on('click', '#delete-grant', function (event) {
                event.preventDefault();
                var clicked_span = $(this);
                delete_form_row(formset, opts, clicked_span);
            });
            $(context).on('change', 'select[name$=-grant_type]',
                          function(event) {
                event.preventDefault();
                fix_grant_subtype_options($(this), true);
            });
            $(context + ' select[name$=-grant_type]').each(function() {
                // In this case, we want the user to see what they previously
                // had as the grant subtype
                fix_grant_subtype_options($(this), false);
            });
            set_default_dates(opts);
        });
    };

    $.fn.gformset.defaults = {
        form_prefix: "",
        formset_class_id: ""
    };

}(jQuery));
