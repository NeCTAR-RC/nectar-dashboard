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
  $('[data-toggle="tooltip"]').tooltip();

  // Is it the login page?
  if($("#splash")) {
    // Stop css animations when
    setTimeout(function(){
      $("#hex-flashing polygon").addClass("paused");
      $("#lines path").addClass("paused");
      $("#lines line").addClass("paused");
    }, 60000);
  }

});