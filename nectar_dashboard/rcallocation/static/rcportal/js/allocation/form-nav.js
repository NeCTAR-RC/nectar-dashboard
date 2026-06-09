/*
 * Allocation request form navigation and layout behaviour.
 *
 * Everything here is scoped to the allocation edit page (#allocationrequest_edit)
 * and drives the two-step wizard layout:
 *
 *   - Page-leave warning / loading-modal handling.
 *   - Accordion panel state (open the first / first-errored panel, highlight
 *     active and error panels).
 *   - Resource bundle selection and the extra-resource toggles.
 *   - Switching between "About the Project" (step 1) and "Cloud Resources"
 *     (step 2), including honouring a #form-step2 URL hash.
 *   - Per-bundle budget estimates based on the project duration.
 */

(function($) {

    var warning_timeout;
    var leaving = false;

    function leaveWarning(event) {
        event.preventDefault();
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
        $(accordion_id + ' > .panel:has(.request-collapse.in)').removeClass("panel-default").addClass('panel-primary');

        // Highlight error panels on page load
        $(accordion_id + ' > .panel:has(div.has-error)').removeClass("panel-default").addClass('panel-danger');

        // Highlight active panel on collapse show event
        $(accordion_id + ' > .panel').on('show.bs.collapse', function() {
            if($(this).hasClass('panel-default')) {
                $(this).removeClass("panel-default");
                $(this).addClass('panel-primary');
            }
            // Remove highlight when not active
            $(accordion_id + ' > .panel').on('hide.bs.collapse', function() {
                if($(this).hasClass('panel-danger')) {
                    $(this).removeClass("panel-danger");
                }
                else {
                    $(this).removeClass("panel-primary");
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
            // reloaded with errors, show custom selected
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

    // The nectar theme sets overflow:hidden on html/body - on dashboard
    // pages the element that actually scrolls is #content_body, not the
    // window. Fall back to the window for other layouts.
    function scrollFormToTop() {
        var $scroller = $('#content_body');
        if ($scroller.length) {
            $scroller.scrollTop(0);
        }
        $(window).scrollTop(0);
    }

    function scrollFormToElement($el, delta) {
        var padding = 20;
        var $scroller = $('#content_body');
        if ($scroller.length) {
            $scroller.scrollTop(Math.max(
                $scroller.scrollTop() + $el.offset().top
                - $scroller.offset().top - delta - padding, 0));
        } else {
            window.scrollTo(0,
                Math.max($el.offset().top - delta - padding, 0));
        }
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
        else if($('#form-step2 .has-error').length
                && !$('#form-step1 .has-error').length) {
            // After a failed submit, open the step containing the
            // validation errors - they would otherwise stay hidden
            // inside the collapsed second step.
            showFormStep(2);
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
            scrollFormToTop();
            showFormStep(2);
        });

        $('.show-form1-button').on('click', function() {
            scrollFormToTop();
            showFormStep(1);
        });

        // Keep the newly-opened panel in view when using the in-panel
        // Next/Previous buttons. Scroll immediately to where the target
        // panel will sit once the accordion transition finishes -
        // waiting for the transition instead lets the browser jump
        // around while the old (tall) panel collapses.
        $('.step-nav a[data-toggle="collapse"]').on('click', function() {
            var $target = $($(this).attr('href'));
            var $panel = $target.closest('.panel');
            var $open = $panel.parent().find('.request-collapse.in');
            // Panels above the target that are open now will have
            // collapsed by the end of the transition. Compare the
            // (always visible) panel frames - the target's collapse
            // div is still display:none here, so its own offset is 0.
            var delta = ($open.length
                         && $open.closest('.panel').offset().top
                            < $panel.offset().top)
                ? $open.outerHeight() : 0;
            scrollFormToElement($panel, delta);
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

    function updateCharCounter($input, $counter) {
        var max = parseInt($input.attr('maxlength'), 10);
        var len = $input.val().length;
        if (len >= max) {
            $counter.text('Character limit reached');
        } else {
            $counter.text(len + ' / ' + max);
        }
        if (max - len <= Math.ceil(max / 10)) {
            $counter.addClass('char-counter-warning');
        } else {
            $counter.removeClass('char-counter-warning');
        }
    }

    // Show a live character counter under every size-limited textarea, so
    // users can see the limit before the browser silently stops their input.
    function initCharCounters() {
        $('textarea[maxlength]').each(function() {
            var $input = $(this);
            if ($input.next('.char-counter').length === 0) {
                var $counter = $(
                    '<small class="char-counter" aria-live="polite" ' +
                    'title="Characters entered / maximum allowed"></small>');
                $input.after($counter);
                updateCharCounter($input, $counter);
            }
        });
    }

    initCharCounters();
    $(document).on('input', 'textarea[maxlength]', function() {
        var $input = $(this);
        var $counter = $input.next('.char-counter');
        if ($counter.length === 0) {
            initCharCounters();
            $counter = $input.next('.char-counter');
        }
        updateCharCounter($input, $counter);
    });
    // Rows added by the publication/grant formsets are built after page load
    $('.publication_formset, .grant_formset').on('click', 'button', function() {
        setTimeout(initCharCounters, 0);
    });

}(jQuery));
