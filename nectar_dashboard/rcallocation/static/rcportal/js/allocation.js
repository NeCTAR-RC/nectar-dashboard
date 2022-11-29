(function($) {

    $('#request_accordion a[data-toggle="collapse"]').click(function(event) {
        // Stop accordion collapse link from adding has to URL
        event.preventDefault();
    });

    // Does the page have errors?
    if($('#request_accordion .has-error')[0]) {
        // Open the first panel with an error
        $(".has-error:first").closest(".request-collapse").addClass("in");
    }
    else {
        // Otherwise, open the first panel
        $("#panelOne").collapse('show');
    }

    // Highlight the active panel on page load
    $('#request_accordion > .panel:has(.request-collapse.in)').removeClass("panel-default").addClass('panel-primary');

    // Highlight error panels on page load
    $('#request_accordion > .panel:has(div.has-error)').removeClass("panel-default").addClass('panel-danger');

    // Highlight active panel on collapse show event
    $('#request_accordion > .panel').on('show.bs.collapse', function () {
        if(!$(this).hasClass('panel-danger')) {
            $(this).removeClass("panel-default");
            $(this).addClass('panel-primary');
        }
    });

    // Remove highlight when not active
    $('#request_accordion > .panel').on('hidden.bs.collapse', function () {
        if($(this).hasClass('panel-danger')) {
            $(this).removeClass("panel-danger");
        }
        else {
            $(this).removeClass("panel-primary");
        }
        $(this).addClass('panel-default');
    });

    function renumber_forms(forms) {
      var match = new RegExp('-\\d+-', 'g');
      forms.each(function (i, item) {
        $(item).find('input, label').each(function() {
          var name = $(this).attr('name');
          if (name) {
            $(this).attr('name', name.replace(match, '-' + i + '-'));
            $(this).attr('id', name.replace(match, '-' + i + '-'));
          }
        });
      });
    };


    function delete_form(item) {
      var form = $(item).closest('.quota-group');
      form.hide();
      form.find('input[id$="-DELETE"]').val(true);
      form.find('input[id$="-requested_quota"]').val(0);
    };


    function create_forms(opts, service_type) {
      var i = $('#quotas-' + service_type).find('.quota-group').length
      var prefix = String.fromCharCode('a'.charCodeAt() + i)

      var r = $('#empty-quotas-' + service_type).find('.quota-group').first().clone();

      r.find('input, label, select').each(function() {
        var name = $(this).attr('name');
        if (name) {
          $(this).attr('name', name.replace(/__prefix__/g, prefix));
          $(this).attr('id', name.replace(/__prefix__/g, prefix));
        }
      });

      r.find('.quota-group-delete').click(function() {
        delete_form($(this));
      });

      $('#quotas-' + service_type).append(r);
      r.show();
    }


    $.fn.formset = function(options) {
      var opts = $.extend({}, $.fn.formset.defaults, options);
      return this.each(function() {

        $('div[id^="quota-resource-"]').each(function() {
          var resource_id = $(this).attr('id').match(/[\d]+$/);
          if (resource_id == null) {
            return
          }
          var resource = opts['resources'][resource_id];
          // Set the labels for the resources
          $(this).find('.label-resource-name').text(resource['name']);
          $(this).find('.label-resource-unit').text(resource['unit']);
          if (resource['help_text']) {
            $(this).find('.label-resource-help').text(resource['help_text']); // admin form
          }
          var popover = $(this).find('.help-popover');
          if (resource['help_text']) {
            popover.attr('title', resource['name']);
            popover.attr('data-content', resource['help_text']);
            popover.show();
          }
          else {
            popover.hide();
          }

          /* Custom hack for RAM!
             Here we add some html to add extra control for the RAM quota.
             We add some radio buttons to ether use default value (= 0) and
             hide the input box or allow a custom value and show it.
          */
          if (resource['quota_name'] == 'ram' && resource['service_type'] == 'compute') {

            var ig = $(this).find('.quota').find('.input-g')
            ig.after('<div class="resource-custom-override">' +
                     '  <label class="radio-inline">' +
                     '    <input type="radio" name="resource_custom_override" value="default">' +
                     '      Default (4GB per core)' +
                     '  </label>' +
                     '  <label class="radio-inline">' +
                     '    <input type="radio" name="resource_custom_override" value="custom">' +
                     '      Custom' +
                     '  </label>' +
                     '</div>');

            var ram_input = ig.find('input');
            var ram_gb = ram_input.val();
            var is_default_ram = (ram_gb == 0);

            // nova project quotas are only available if a project exists
            // already, and the form isn't being returned due to an error
            if ('quota_limits' in opts) {
              var quota_limits = opts['quota_limits'];
              if ('maxTotalRAMSize' in quota_limits) {
                ram_gb = parseInt(quota_limits['maxTotalRAMSize'] / 1024);
                num_cores = parseInt(quota_limits['maxTotalCores']);
                is_default_ram = (ram_gb == num_cores * 4);
              }
            }

            // if ram value is default (e.g. cores x 4 or 0) then hide the
            // input field and choose the default radio setting, otherwise
            // choose the custom setting and set the value in the input
            var radio_override = $(this).find('input:radio[name="resource_custom_override"]')
            if (is_default_ram) {
              radio_override.val(['default']);
              ig.hide();
            } else {
              radio_override.val(['custom']);
              ram_input.val(ram_gb);
            }
          }
        });

        $('input[name="resource_custom_override"]').change(function(){
          var ig = $(this).closest('.controls').find('.input-g');

          if ($(this).val() == 'custom') {
            ig.show();
          }
          else {
            // Reset to 0 as its what the default value is
            ig.find('input').val(0);
            ig.hide();
          }
        });

        $('input:checkbox.toggle-quota').change(function() {
          var panel = $(this).closest('.panel');
          var enabled = this.checked;
          panel.find('.panel-collapse').collapse(this.checked ? 'show' : 'hide');

          // Set quotas to 0 if service is disabled
          if (!enabled) {
            panel.find('input[id$="-requested_quota"]').each(function() {
              $(this).val(0);
            });
          }

          // Set the value of hidden input field called enabled
          panel.find('input.quota-group-enabled').each(function() {
            $(this).val(enabled);
          });
        });


        $(this).find('div[id^="panel-quota-"]').each(function() {
          var id = $(this).attr('id');
          var service_type = id.match(/^panel-quota-([\w-]+)$/)[1];
          var zones = opts['service_types'][service_type]['zones']

          /* If this is a multi-zone resource, show the 'Add more' button */
          if (zones.length > 1) {
            $('input[id^="add-quota-' + service_type + '"]').show();
          } else {
            $('input[id^="add-quota-' + service_type + '"]').hide();
          }

          var is_enabled = false;
          if (service_type == "rating") {
            is_enabled = true;
          } else {
            $(this).find('input[id$="-requested_quota"]').each(function() {
              if (this.value > 0) {
                is_enabled = true;
             }
            });
          }

          var toggle = $(this).find('input:checkbox.toggle-quota');
          if (toggle.length) {
            $(this).find('div.panel-collapse').collapse(is_enabled ? 'show' : 'hide');
            toggle.prop('checked', is_enabled).change();
          }
        });

        $('input[id^="add-quota-"]').click(function() {
          var id = $(this).attr('id');
          var service_type = id.match(/^add-quota-([\w-]+)$/)[1];
          create_forms(opts, service_type);
        });

      });
    };

    // Plugin defaults – added as a property on our plugin function.
    $.fn.formset.defaults = {
       prefix: "",
       service_types: {},
       resources: {},
       zones: {},
    };
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

// Organizations formset
(function($) {

    function create_form_row(formset, opts) {
        if(opts.show_label == true){
            show_label_div(opts);
        }
        var total_rows = $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').length;
        var form_new_row = create_row(opts.prefix, total_rows, opts);
        $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first').append(form_new_row);
        total_rows +=1;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
    };

    function show_label_div(opts){
        var label_div = $('div.'+ opts.formset_class_id + ' div.label_header');
        label_div.attr('class','label_header');
    }

    function hide_label_div(opts){
        var label_div = $('div.'+ opts.formset_class_id + ' div.label_header');
        label_div.attr('class','label_header hidden');
    }

    function create_row(prefix, count, opts){
        var new_row = "<fieldset>";
        new_row += "<input id='id_" + prefix + "-" + count + "-id' name='" + prefix + "-" + count + "-id' type='hidden'>";
        new_row += "<input id='id_" + prefix + "-" + count + "-DELETE' type='hidden' value='false' name='" + prefix + "-" + count + "-DELETE'>";
        new_row += "<div class='flex-group form-group'>";
        var input_style_css = opts.input_style_css;
        if (input_style_css != ''){
            new_row += "<div class='input-g " + input_style_css +"'>";
        }else{
            new_row += "<div class='input-g'>";
        }
        new_row += "<input class='form-control' id='id_" + prefix + "-" + count + "-" + opts.field_name + "' maxlength='255' name='" + prefix + "-" + count + "-" + opts.field_name + "' type='text'>";
        new_row += "</div>";
        new_row += "<span title='remove' id='id_" + prefix + "-" + count + "-" + opts.field_name +"' class='delete-icon-sp text-danger'> &nbsp; &nbsp;<i class='fa fa-times'></i> &nbsp; &nbsp; </span>"
        new_row += "</div>";
        new_row += "</fieldset>";
        return new_row;
    };

    function delete_form_row(formset, opts, span){
        var span_id = span.attr('id');
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
        var total_hidden_rows = $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset.hidden').length;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
        if ((total_rows == 0 || total_rows == total_hidden_rows ) && opts.show_label == true){
            hide_label_div(opts);
        }
    };

    function resort_form_rows(formset, opts){
        $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').each(function() {
            var current_index = this.rowIndex;

            //reindex the id input field
            var id_input = $(this).find('input[id$=-id]');
            id_input.attr('id','id_' + opts.prefix + '-' + current_index + '-id' );
            id_input.attr('name', opts.prefix + '-' + current_index + '-id');

            //reindex the delete input field
            var id_input = $(this).find('input[id$=-DELETE]');
            id_input.attr('id','id_' + opts.prefix + '-' + current_index + '-DELETE' );
            id_input.attr('name', opts.prefix + '-' + current_index + '-DELETE');

            //reindex the name input field
            var name_input = $(this).find('input[id$=-' + opts.field_name + ']');
            var new_id = 'id_' + opts.prefix + '-' + current_index + '-' + opts.field_name;
            name_input.attr('id', new_id);
            name_input.attr('name', opts.prefix + '-' + current_index + '-' + opts.field_name);

            //reindex the span
            var span_del = $(this).find('span[id$=-' + opts.field_name +']');
            span_del.attr('id',new_id );
        });
    };

    $.fn.mformset = function(options) {
        var opts = $.extend( {}, $.fn.mformset.defaults, options );

         return this.each(function() {
             //set current formset
             var formset = this;
             $('div.' + options.formset_class_id).on('click', '#add_another', function (event) {
                 event.preventDefault();
                 create_form_row(formset, opts);
                 apply_popover();
             });

             $('div.'+ options.formset_class_id).on('click', '.delete-icon-sp', function (event){
                 event.preventDefault();
                 var clicked_span = $(this);
                 delete_form_row(formset, opts, clicked_span);
             });
         });
    };

    $.fn.mformset.defaults = {
        form_prefix: "",
        formset_class_id: "",
        field_name:"",
        input_style_css:"",
        show_label: false
    };

}(jQuery));

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

        $('div.'+ opts.formset_class_id + ' div.more_fields_tab > div:first fieldset').each(function() {
            var current_index = this.rowIndex;
            //reindex the id input field
            var id_input = $(this).find('input[id$=-id]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + current_index + '-id');
            id_input.attr('name', opts.prefix + '-' + current_index + '-id');
            //reindex the delete input field
            var id_input = $(this).find('input[id$=-DELETE]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + current_index + '-DELETE');
            id_input.attr('name', opts.prefix + '-' + current_index + '-DELETE');

            //reindex the label for
            $(this).find("label[for^='id_" + opts.prefix + "-']").each(function(){
                var labelFor = $(this).attr('for').replace(match, opts.prefix +'-' + current_index + '-');
                $(this).attr('for', labelFor);
            });

            //reindex select id and name
            $(this).find("select.form-control").each(function(){
                var selectId = $(this).attr('id').replace(match, opts.prefix + '-' + current_index + '-');
                var selectName = $(this).attr('name').replace(match, opts.prefix + '-' + current_index + '-');
                $(this).attr('id', selectId);
                $(this).attr('name', selectName);
            });

            //reindex the input id and name
            $(this).find("input.form-control").each(function(){
                var inputId = $(this).attr('id').replace(match, opts.prefix + '-' + current_index + '-');
                var inputName = $(this).attr('name').replace(match, opts.prefix + '-' + current_index + '-');
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
        var total_rows = $('div.'+ opts.formset_class_id + ' table > tbody > tr').length;
        var form_new_row = create_row(opts.prefix, total_rows, opts);
        $('div.'+ opts.formset_class_id + ' table > tbody:last').append(form_new_row);
        var new_row_id = 'id_' + opts.prefix + '-' + total_rows + '-id';
        var new_row_tr = $('input[id=' + new_row_id + ']').closest('tr');
        apply_pub_handlers(new_row_tr);
        init_pub_form_visibility(new_row_tr, '', true);
        total_rows += 1;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
    };

    function create_row(prefix, row_index, opts){
        var new_row = "<tr>";
        new_row += "<td>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-id' id='id_" + opts.prefix + "-" + row_index + "-id'>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-DELETE' id='id_" + opts.prefix + "-" + row_index + "-DELETE'>";
        new_row += "<input type='hidden' name='" + opts.prefix + "-" + row_index + "-crossref_metadata' id='id_" + opts.prefix + "-" + row_index + "-crossref_metadata'>";
        new_row += "</td>";
        new_row += "<td>";
        new_row += "<div class='publication_div'>";
        //output_type
        new_row += create_field_div(opts, 'output_type', row_index, '');
        new_row += create_input_field_label(opts, 'output_type', 'Research Output type', row_index, false, "Select a publication type that best describes the publication.  The 'Media publication' type is intended to encompass traditional media and 'new' media such as websites, blogs and social media.");
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
        //doi prompts
        new_row += "<div name='prompts-group' hidden>";
        new_row += "<div>";
        new_row += "Recently published books and peer reviewed papers have a ";
        new_row += "Digital Object Identifier (DOI) issued by the publisher. ";
        new_row += "We need you to enter that DOI (if it exists) and ";
        new_row += "validate it.  If you do not have the DOI to hand, you ";
        new_row += "should be able to find it by doing a Crossref search. ";
        new_row += "In the event that there is no validatable DOI, you ";
        new_row += "will need to (re-)enter the citation details by hand.";
        new_row += "<br><br>";
        new_row += "<button type='button' name='have-doi' class='btn btn-default'>";
        new_row += "I have a DOI to enter";
        new_row += "</button>&nbsp;";
        new_row += "<button type='button' name='no-doi' class='btn btn-default'>";
        new_row += "This publication has no DOI";
        new_row += "</button>&nbsp;";
        new_row += "<button type='button' class='btn btn-default' onClick='window.open(\"https://search.crossref.org/\");'>";
        new_row += "Open Crossref Search window";
        new_row += "</button>";
        new_row += "</div>";
        new_row += "</div>";
        //doi
        new_row += create_field_div(opts, 'doi', row_index, 'hidden');
        new_row += create_input_field_label(opts, 'doi', 'Digital Object Identifier(DOI)', row_index, false, "Provide the Research Output's DOI. A DOI should be provided for all books and peer-reviewed papers. A valid DOI starts with '10.&lt;number&gt;/'. This is followed by letters, numbers and other characters. For example: '10.23456/abc-123'.");
        new_row += "<div class='controls'>";
        new_row += "<div class='form-inline'>";
        new_row += "<div class='input-g'>";
        new_row += create_input_field(opts, 'doi', 'text',
                                      'style="width:420px" maxlength="256"',
                                      row_index);
        new_row += "<button type='button' id='check-doi' class='pull-right btn btn-default'>";
        new_row += "Validate DOI";
        new_row += "</button>";
        new_row += "</div>";
        new_row += "</div>";
        new_row += "</div>";
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
        new_row += "<div name='details-group'>";
        new_row += "<label>Crossref details</label>";
        new_row += "<div name='details-text'>";
        new_row += "</div>";
        new_row += "</div>";
        // closed details div
        new_row += "</div>"
        new_row += "</td>";
        new_row += "<td>";
        new_row += "<button type='button' id='delete-publication' class='pull-right btn btn-default'>";
        new_row += "Delete";
        new_row += "</button>";
        new_row += "</td>";
        new_row += "</tr>";
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
        var current_tr = span.closest('tr');
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
        var total_rows = $('div.'+ opts.formset_class_id + ' table > tbody > tr').length;
        var total_forms_input = $('#id_' + opts.prefix + '-TOTAL_FORMS');
        total_forms_input.val(total_rows);
    };

    function check_doi(span){
        var current_tr = span.closest('tr');
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

        $('div.'+ opts.formset_class_id + ' table > tbody > tr').each(function() {
            var current_index = this.rowIndex;
            //reindex the id input field
            var id_input = $(this).find('input[id$=-id]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + current_index + '-id');
            id_input.attr('name', opts.prefix + '-' + current_index + '-id');
            //reindex the delete input field
            var id_input = $(this).find('input[id$=-DELETE]');
            id_input.attr('id', 'id_' + opts.prefix + '-' + current_index + '-DELETE');
            id_input.attr('name', opts.prefix + '-' + current_index + '-DELETE');

            //reindex the label for
            $(this).find("label[for^='id_" + opts.prefix + "-']").each(function(){
                var labelFor = $(this).attr('for').replace(match, opts.prefix +'-' + current_index + '-');
                $(this).attr('for', labelFor);
            });

            //reindex select id and name
            $(this).find("select.form-control").each(function(){
                var selectId = $(this).attr('id').replace(match, opts.prefix + '-' + current_index + '-');
                var selectName = $(this).attr('name').replace(match, opts.prefix + '-' + current_index + '-');
                $(this).attr('id', selectId);
                $(this).attr('name', selectName);
            });

            //reindex the input id and name
            $(this).find("input.form-control").each(function(){
                var inputId = $(this).attr('id').replace(match, opts.prefix + '-' + current_index + '-');
                var inputName = $(this).attr('name').replace(match, opts.prefix + '-' + current_index + '-');
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
             $('div.' + options.formset_class_id + ' tr').each(function (){
                 var tr = $(this);
                 var output_group = tr.find('div[id$=-output_type-group]');
                 if (!output_group.attr('hidden')) {
                     var output_type = tr.find('select[id$=-output_type]');
                     apply_pub_handlers(tr);
                     init_pub_form_visibility(tr, output_type.val(), false);
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

function init_pub_form_visibility(tr, output_type, type_changed) {
    var prompts_group = tr.find('div[name=prompts-group]');
    var doi_group = tr.find('div[id$=-doi-group]');
    var doi_input = tr.find('input[id$=-doi]');
    var details_group = tr.find('div[name=details-group]');
    var meta_input = tr.find('input[id$=-crossref_metadata]');
    var pub_group = tr.find('div[id$=-publication-group]');
    var pub_input = tr.find('input[id$=-publication]');
    if (output_type == 'AJ' || output_type == 'AP' ||
        output_type == 'AN' || output_type == 'B') {
        if (!doi_input.val()) {
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
        } else if (meta_input.val()) {
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
    tr.off('change', 'select[id$=-output_type]');
    tr.on('change', 'select[id$=-output_type]', function(e) {
        var output_type = $(this).val();
        var current_tr = $(this).closest('tr');
        init_pub_form_visibility(current_tr, output_type, true);
    });
    tr.off('change', 'input[id$=-doi]');
    tr.on('change', 'input[id$=-doi]', function(e) {
        tr.find('input[id$=-crossref_metadata]').val('');
        tr.find('div[name=details-group]').hide();
    });
    tr.off('click', 'button[name=have-doi]');
    tr.on('click', 'button[name=have-doi]', function(e) {
        var current_tr = $(this).closest('tr');
        current_tr.find('div[name=prompts-group]').hide();
        current_tr.find('div[id$=-doi-group]').show();
        current_tr.find('div[name=details-group]').hide()
        current_tr.find('div[id$=-publication-group]').hide();
    });
    tr.off('click', 'button[name=no-doi]');
    tr.on('click', 'button[name=no-doi]', function(e) {
        var current_tr = $(this).closest('tr');
        current_tr.find('div[name=prompts-group]').hide();
        current_tr.find('div[id$=-doi-group]').hide();
        current_tr.find('div[name=details-group]').hide()
        current_tr.find('div[id$=-publication-group]').show();
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
        $('#doi-accept').show();
        $('#doi-reject').show();
        $('#doi-close').hide();
    } else {
        $('#doi-found').hide();
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
    var tr = crossref_input.closest('tr');
    var details = tr.find('div[name=details-text]');
    var metadata = $('#doi-crossref').val();
    crossref_input.val(metadata);
    details.html(render_crossref_metadata(metadata));
    tr.find('div[id$=-publication-group]').hide();
    tr.find('div[name=details-group]').show();
};

function reject_doi(e) {
    e.preventDefault();
    var row_no = $('#doi-row').val();
    var doi = $('#doi-doi').val();
    var crossref_input = $('#id_publications-' + row_no + '-crossref_metadata');
    var tr = crossref_input.closest('tr');
    var details = tr.find('div[name=details-text]');
    crossref_input.val('');
    details.html("No information available for DOI " + doi);
    tr.find('div[id$=-publication-group]').show();
    tr.find('div[name=details-group]').hide();
};

$('#doi-close').click(reject_doi);
$('#doi-reject').click(reject_doi);
$('#doi-accept').click(accept_doi);

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
