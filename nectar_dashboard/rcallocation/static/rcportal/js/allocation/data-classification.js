/*
 * Data sensitivity / classification behaviour.
 *
 * Runs on DOMContentLoaded and wires up the data-handling part of the form:
 *
 *   - "Multiple allocations" toggle: show/hide the toggleable fields and add a
 *     required asterisk to their labels when shown.
 *   - Sensitive-data dropdown (#id_has_sensitive_data) drives the data
 *     classification level (#id_data_classification_level): forces green/not_sure
 *     for non-sensitive/unknown, greys out the green option for sensitive data,
 *     and shows the institutional data-review field when data is sensitive.
 *   - Keeps the hidden classification field in sync (incl. before submit) and
 *     updates the colour-coded description box for the selected level.
 *   - Renders read-only classification description boxes (.data-classification-box)
 *     from their data-value.
 */

document.addEventListener('DOMContentLoaded', function() {
    function addAsterisk(label) {
        // Check if the asterisk already exists
        if (label.querySelector('.glyphicon.glyphicon-asterisk.text-secondary')) {
            return;
        }
        var asterisk = document.createElement('span');
        asterisk.className = 'glyphicon glyphicon-asterisk text-secondary';
        var img = label.querySelector('img');
        if (img) {
            label.insertBefore(asterisk, img);
        } else {
            label.appendChild(asterisk);
        }
    }

    function toggleFields() {
        var selectField = document.getElementById("id_multiple_allocations_check");
        var fields = document.getElementsByClassName("toggleable");

        var selectedValue = selectField.value;

        for (var i = 0; i < fields.length; i++) {
            if (selectedValue == "True"){
                fields[i].style.display = "none";
            } else {
                fields[i].style.display = "block";
                addAsterisk(fields[i].querySelector('label'))
            }
        }
    }

    var selectField = document.getElementById("id_multiple_allocations_check");
    if (selectField) {
        selectField.addEventListener("change", toggleFields);
        toggleFields();  // Initial call to set the correct visibility
    }

    var sensitiveData = document.getElementById('id_has_sensitive_data');
    var dropdown = document.getElementById('id_data_classification_level');
    var hiddenField = document.getElementById('id_data_classification_level_hidden');
    var targetBox = document.getElementById('data-classification-box');
    var institutionalReviewContainer = document.getElementById('institutional_data_review_container');

    function setImpactField() {
        var sensitiveValue = sensitiveData.value;
        var userSelectedValue = dropdown.value;  // Preserve user selection

        // Handle institutional review visibility
        if (sensitiveValue === 'sensitive') {
            institutionalReviewContainer.style.display = 'block';
            // Add asterisk to the label when shown
            var label = institutionalReviewContainer.querySelector('label');
            addAsterisk(label);
        } else {
            institutionalReviewContainer.style.display = 'none';
            // Reset the institutional_data_review value when hidden
            document.getElementById('id_institutional_data_review').value = '';
        }

        // First, ensure all options are visible and enabled
        Array.from(dropdown.options).forEach(option => {
            option.disabled = false;
            option.style.display = '';
        });

        if (sensitiveValue == 'no_sensitive') {
            dropdown.value = 'green';
            dropdown.disabled = true;
        } else if (sensitiveValue == 'unknown') {
                   dropdown.value = 'not_sure';
                   dropdown.disabled = true;
        } else {
            dropdown.disabled = false;
            // For sensitive data, disable and grey out green option
            Array.from(dropdown.options).forEach(option => {
                if (option.value === 'green') {
                    option.disabled = true;
                    option.style.color = '#999';  // Grey color
                    option.style.backgroundColor = '#f5f5f5';  // Light grey background
                }
            });
            // If the user has selected a value, don't reset it
            if (!dropdown.dataset.userSelected) {
                dropdown.value = userSelectedValue;
            }
            // If current value is green, reset to default empty option
            if (userSelectedValue === 'green') {
                dropdown.value = '';
            }
        }

        // Ensure hidden field is always updated
        hiddenField.value = dropdown.value;

        dropdown.dispatchEvent(new InputEvent("input",  { bubbles: true }));
        dropdown.dispatchEvent(new Event("change",  { bubbles: true }));
    }

    // For setting the data sensitivity description
    const descriptions = {
        'green': {
            text: 'Data misuse would have little to no impact.',
            border: '2px solid #39833E'
        },
        'yellow': {
            text: 'Data misuse unlikely to cause harm or have a negligible adverse impact.',
            border: '2px solid #F8B20E'
        },
        'orange': {
            text: 'Data breach or misuse may have a major adverse impact to your organisation ' +
                  'or an external party. Unauthorised release of data could be a regulatory offence.',
            border: '2px solid #F6861F'
        },
        'red': {
            text: 'Data breach or misuse is expected to cause severe harm to your organisation ' +
                  'or an external party. Unauthorised release of data could be a regulatory or ' +
                  'criminal offence.',
            border: '2px solid red'
        },
    };

    // Function to update the description text and color
    function updateDescriptionBox() {
        var selectedValue = dropdown.value;
        var description = descriptions[selectedValue] || {
            text: '',
            border: '0px',
        };

        // Update the text and background color of the box
        if (description.text == '') {
            targetBox.style.display = "none"
        } else {
            targetBox.style.display = "block"
            targetBox.textContent = description.text;
            targetBox.style.border = description.border;
        }
    }

    if (sensitiveData && dropdown && targetBox) {
        // Attach event listener for changes in the dropdowns
        sensitiveData.addEventListener('change', setImpactField);

        dropdown.addEventListener('change', function () {
           dropdown.dataset.userSelected = "true"; // Mark that user has manually selected a value
           hiddenField.value = dropdown.value;
           updateDescriptionBox();
        });

        // Initial update on page load
        setImpactField();

       var form = dropdown.closest("form");
       // Ensure hidden field is updated before form submission
       form.addEventListener('submit', function () {
           hiddenField.value = dropdown.value;
       });
    }

    var dataBoxes = document.querySelectorAll('.data-classification-box');
    dataBoxes.forEach(function(dataBox) {
        var displayedValue = dataBox.dataset.value; // Get the value dynamically set by Django
        var displayData = descriptions[displayedValue] || {
            text: '',
        };

        if (displayData.text == '') {
            dataBox.style.display = "none"
        } else {
            dataBox.textContent = displayData.text;
            dataBox.style.border = displayData.border;
        }
    });
});
