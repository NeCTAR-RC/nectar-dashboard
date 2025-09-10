/* Function to convert string to number with 2 decimal places */
function convertToFloat(str_num) {
  return Math.round(Number(str_num) * 100) / 100;
}

/* Function to get the project usage to date from api request */
function getUsageTotal() {
  $.ajax({
    url: "/api/nectar/allocation/usage/",
    type: 'GET',
    dataType: 'JSON',
    success: function(data) {
      //console.log(data);
      if(data[0].rate) {
        var project_su_used = convertToFloat(data[0].rate);
        $("#project_su_used").text(project_su_used);
      }
    },
    error: function (xhr, ajaxOptions, thrownError) {
      console.error(xhr.status + " " + thrownError);
      return false;
    }
  });
}

/* Function to get the project usage budget from api request */
function getUsageBudget() {
  $.ajax({
    url: "/api/nectar/allocation/su-budget/",
    type: 'GET',
    dataType: 'JSON',
    success: function(data) {
      if(data) {
        var project_su_budget = data;
        if(project_su_budget === -1) {
          $("#project_su_budget").text("Unlimited");
        }
        else {
          $("#project_su_budget").text(project_su_budget);
        }
      }
    },
    error: function (xhr, ajaxOptions, thrownError) {
      console.error(xhr.status + " " + thrownError);
    }
  });
}

/* Function to get the current bundle for the project allocation  */
function getCurrentBundle() {
  var api_url = "/api/nectar/allocation/current/";
  $.ajax({
    url: api_url,
    type: 'GET',
    dataType: 'JSON',
    success: function(data) {
      console.log(data);
      if(data.bundle) {
        let bundle = data.bundle;
        $("#current_bundle").text(bundle);
      }
      else {
        $("#current_bundle").text("Custom");
      }
    },
    error: function(xhr, ajaxOptions, thrownError){
      console.error(api_url + " " + xhr.status + " " + thrownError);
    }
  });
}

/* Survey Monkey popup invitation */

/* Check if the survey has been shown today */
function isSurveyShownToday(today) {
const lastShown = sessionStorage.getItem('surveyMonkeyPopupShown');
return lastShown === today;
}

/* Set the survey as shown today */
function setSurveyShownToday(today) {
  sessionStorage.setItem('surveyMonkeyPopupShown', today);
}

/* Set that user has clicked the survey link */
function setSurveyLinkClicked() {
  sessionStorage.setItem('surveyLinkClicked', 'true');
}

/* Check if user has NOT clicked the survey link */
function surveyNotClicked() {
  return sessionStorage.getItem('surveyLinkClicked') !== 'true';
}

/* Calculate time remaining until 11:45pm on September 15, 2025 */
function getTimeUntilCutoff() {
  const cutoffDate = new Date('2025-09-15T23:45:00+10:00');
  const today = new Date();
  const timeDiff = cutoffDate.getTime() - today.getTime();

  if (timeDiff <= 0) {
    return { days: 0, hours: 0, minutes: 0 };
  }

  const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));

  return { days, hours, minutes };
}

function showSurveyInviteModal(userIsLoggedIn) {

  /* Check if today's date is before or equal to 2025-09-15 */
  const cutoffDate = new Date('2025-09-15');
  const today = new Date();
  const todayString = today.toDateString();

  if(today <= cutoffDate && userIsLoggedIn && !isSurveyShownToday(todayString) && surveyNotClicked()) {
    // Update countdown display
    const timeLeft = getTimeUntilCutoff();
    $('#countdown-days').text(timeLeft.days);
    $('#countdown-hours').text(timeLeft.hours);
    $('#countdown-minutes').text(timeLeft.minutes);

    $('#survey_invite_modal').modal('show');
      $('#survey_invite_yes_button').on('click', function() {
        setSurveyLinkClicked();
        window.open('https://www.surveymonkey.com/r/Nectar2025', '_blank');
      });
    $('#survey_invite_no_button').on('click', function() {
      $('#survey_invite_modal').modal('hide');
    });
    setSurveyShownToday(todayString);
  }
}

$(document).ready(function() {

  // Add slideDown animation to Bootstrap dropdown when expanding.
  $('.dropdown').on('show.bs.dropdown', function() {
    $(this).find('.dropdown-menu').first().stop(true, true).slideDown();
  });

  // Add slideUp animation to Bootstrap dropdown when collapsing.
  $('.dropdown').on('hide.bs.dropdown', function() {
    $(this).find('.dropdown-menu').first().stop(true, true).slideUp();
  });

  // Activate Bootstrap 3 tooltips
  $('[data-toggle="tooltip"]').tooltip({ container: 'body' });

  // Is it the login page?
  if($("#splash").length) {
    // Stop css animations when
    setTimeout(function(){
      $("#hex-flashing polygon").addClass("paused");
      $("#lines path").addClass("paused");
      $("#lines line").addClass("paused");
    }, 60000);
  }

  if($("#project_info").length) {
    getCurrentBundle();
    getUsageTotal();
    getUsageBudget();
  }
});
