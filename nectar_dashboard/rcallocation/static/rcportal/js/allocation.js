(function($) {

    var warning_timeout;
    var leaving = false;

    function leaveWarning(event) {
        if($.browser.mozilla) { event.preventDefault(); }
        warning_timeout = setTimeout(function() {
            if(leaving === false) { hideLoadingModal() };
        }, 3000);
        return (event.returnValue = "");
    }

    function noTimeout() {
        leaving = true;
        clearTimeout(warning_timeout);
    }

    // Hides the horizon page loader which is displayed when the user clicks a link.
    function hideLoadingModal() {
        $("#modal_wrapper > .modal.loading").remove();
        $(".modal-backdrop.in").remove();
        $("body").removeClass("modal-open");
    }

    function setPanelStates(accordion_id) {
        $(accordion_id + ' a[data-toggle="collapse"]').click(function(event) {
            // Stop accordion collapse link from adding hash to URL
            event.preventDefault();
        });

        // Does the page have errors?
        if($(accordion_id + ' .has-error')[0]) {
            // Open the first panel with an error
            $(".has-error:first").closest(".request-collapse").addClass('in');
        }
        else {
            // Otherwise, open the first panel
            $(accordion_id + " .request-collapse:first").addClass('in');
        }

        // Highlight the active panel on page load
        $(accordion_id + ' > .panel:has(.request-collapse.in)').removeClass("panel-default").addClass('panel-warning');

        // Highlight error panels on page load
        $(accordion_id + ' > .panel:has(div.has-error)').removeClass("panel-default").addClass('panel-danger');

        // Highlight active panel on collapse show event
        $(accordion_id + ' > .panel').on('show.bs.collapse', function() {
            if($(this).hasClass('panel-default')) {
                $(this).removeClass("panel-default");
                $(this).addClass('panel-warning');
            }
            // Remove highlight when not active
            $(accordion_id + ' > .panel').on('hide.bs.collapse', function() {
                if($(this).hasClass('panel-danger')) {
                    $(this).removeClass("panel-danger");
                }
                else {
                    $(this).removeClass("panel-warning");
                }
                $(this).addClass('panel-default');
            });
        });
    }

    function setActiveResources() {
        var isExistingRequest = $("#allocationrequest_edit").hasClass("allocation-existing") ? true : false;
        var isNewWithErrors = $("#allocationrequest_edit").hasClass("allocation-new-errors") ? true : false;

        if($('select#id_bundle').val()) {
            // Show previously selected bundle as selected
            $('.bundle[data-bundle=' + $('select#id_bundle').val() + ']').addClass('active');
        }
        else if(isExistingRequest || isNewWithErrors) {
            // If no bundle previously selected, and
            // it's an existing request or the page has
            // relaoded with errors, show custom selected
            $('.bundle:last').addClass('active');
        }
        else {
            // Select standard bundle if it's a new request
            // and no bundle previously selected
            $('.bundle:first').addClass('active');
            $('select#id_bundle').val($('.bundle:first').data('bundle'));
        }

        $('.resource-zone').each(function() {
            if($(this).find('input').val() > 0) {
                $(this).closest('.extra-resource').find('.resource-toggle').bootstrapToggle('on');
                $(this).closest('.extra-resource').find('fieldset').show();
            }
        });
    }

    function showFormStep(formSectionId) {
        if(formSectionId == 2) {
            $('section#form-step1').hide();
            $('section#form-step2').show();
            $("#form-step-title").text("Cloud Resources");
            $('#allocation_form_nav li.active').removeClass('active');
            $('#allocation_form_nav li:nth-child(2)').addClass('active');
        }
        else {
            $('section#form-step2').hide();
            $('section#form-step1').show();
            $("#form-step-title").text("About the Project");
            $('#allocation_form_nav li.active').removeClass('active');
            $('#allocation_form_nav li:first').addClass('active');
        }
    }

    function setBudgets() {
        let duration = $("#id_estimated_project_duration").val();
        let durationStr = "year";

        if(duration == 1) {
            durationStr = "month";
        } else if(duration > 1 && duration < 12) {
            durationStr = duration + " months";
        }
        
        $('.bundle').each(function() {
            if($(this).data('suyear')) {
                let budget = $(this).data('suyear') / 12 * duration;
                $(this).find('.bundle-budget').text(parseInt(budget));
                $(this).find('.bundle-duration').text(durationStr);
            }
        });
    }

    if($("#allocationrequest_edit").length) {
        setPanelStates("#request_accordion");
        setPanelStates("#resources_accordion");
        setActiveResources();
        setBudgets();
        $("#id_estimated_project_duration").on("change", function() { setBudgets() });

        if(window.location.hash) {
            var pageHash = window.location.hash.substring(1);
            console.log(pageHash);
            if(pageHash == "form-step2" || pageHash == "!#form-step2") {
                showFormStep(2);
            }
            else {
                showFormStep(1);
            }
        }
        else {
            showFormStep(1);
        }

        $('.show-form2-button').on('click', function() {
            // Did the user click the continue button?
            if($(this).hasClass("continue-button")) {
                // Is the first panel currently collapsed?
                if(!$("#resources_accordion .request-collapse:first").hasClass("in")) {
                    // Collapse any other open panels
                    $("#resources_accordion .request-collapse.in").collapse('hide').on('hidden.bs.collapse', function () {
                        // Open the first panel
                        $("#resources_accordion .request-collapse:first").collapse('show');
                    });
                }
            }
            $(window).scrollTop(0);
            showFormStep(2);
        });

        $('.show-form1-button').on('click', function() {
            $(window).scrollTop(0);
            showFormStep(1);
        });

        $('.bundle > .btn').on('click', function(e) {
            e.preventDefault();
            var clickedBundle = $(this).closest('.bundle');
            if(clickedBundle.hasClass('active') === false) {
                $('.bundle.active').removeClass('active');
                clickedBundle.addClass('active');
                $('select#id_bundle').val(clickedBundle.data('bundle'));
            }
        });

        $('.resource-toggle').each(function() {
            $(this).change(function() {
                var toggleFields = $(this).closest('.extra-resource').find('fieldset');
                if(toggleFields.is(":hidden")) {
                    toggleFields.slideDown();
                }
                else {
                    toggleFields.slideUp();
                }
            });
        });

        // Set a leave alert warning on the allocation form page
        $(window).bind('beforeunload', leaveWarning);
        $(window).bind('unload', noTimeout);
        $('form .submit-form-button').click(function() {
            $(window).unbind('beforeunload');
        });
    }

}(jQuery));

function apply_popover() {
  // Popover tooltip settings - note we use a manual trigger to support keeping
  // the popup open to allow clicking hyperlinks within the text
  $('.help-popover').popover({
    trigger: "manual",
    placement: "top",
    html: true,
    animation: false,
  })
  .on("mouseenter", function() {
    var _this = this;
    $(this).popover("show");
    $(".popover").on("mouseleave", function() {
      $(_this).popover('hide');
    });
  })
  .on("mouseleave", function() {
    var _this = this;
    setTimeout(function() {
      if (!$(".popover:hover").length) {
        $(_this).popover("hide");
      }
    }, 200);
  });
}

function get_dns_service_name(project_name) {
  var domain_name = 'cloud.edu.au';
  var zone;

  // Setting an arbitary length for new project names to >=5
  if (project_name.length < 5) {
    zone = '';
  } else {
    // Copied from nectar-tools/expiry/archiver.py
    var name = project_name.toLowerCase()
                           .replace(/_/g, '-')
                           .replace(/[^a-z0-9-]+/g, '')
                           .replace(/(-)\1+/g, '$1')
                           .replace(/^[^a-z0-9]/g, '')
                           .substring(0, 62)
                           .replace(/[^a-z0-9]$/g, '');
    zone = name + '.' + domain_name;
  }
  return zone;
}

function populate_dns_service_name() {
  if ($('#id_project_name').length) {
    var project_name = $('#id_project_name').val();
    var zone = get_dns_service_name(project_name);
    $('#id_dns_domain').val(zone);
  }
}

$('#id_project_name').on('input', function(e) {
  populate_dns_service_name();
});


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
             ["rdc", "Rural Research and Developmemt Corporation"],
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
             ["nhmrc-mrff", "NHMRC Medical Research Future Fund"],
             ["nhmrc-pc", "NHMRC Partnership Centre"],
             ["nhmrc-pp", "NHMRC Partnership project"],
             ["nhmrc-tcr", "NHMRC Targeted Calls for Research"],
             ["nhmrc-iriiss", "NHMRC Independent Research Institute Infrastructure Support Scheme"],
             ["nhmrc-bdri", "NHMRC Boosting Dementia Research Initiatives (various)"],
             ["nhmrc-other", "Other NHMRC scheme"],
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
        new_row += create_input_field(opts, 'funding_body_scheme', 'Funding body and scheme', row_index);
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

    function create_input_field(opts, field_name, field_label, row_index){
        return "<input type='text' name='" + opts.prefix + "-" + row_index + "-" + field_name + "' maxlength='200' id='id_" + opts.prefix + "-" + row_index + "-" + field_name + "' class='form-control'>";
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
            // Treat this as a mis-click
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

function escapeText(value) {
    return value.toString().replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

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

function submit_ignore() {
    // Submit the allocation form with the hidden field set to tell the
    // server side to not to check for quota sanity and other warnings.
    document.getElementById("id_ignore_warnings").value = '1';
    document.getElementById("new-allocation").submit();   // sic
}
