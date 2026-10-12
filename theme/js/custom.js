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
