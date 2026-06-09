/*
 * Shared utilities for the allocation request form.
 *
 * These helpers are used across the other allocation form scripts, so this
 * file must be loaded before them.
 *
 *   - escapeText():   HTML-escape a string for safe insertion into markup.
 *   - apply_popover(): (re)initialise the Bootstrap help popovers, including
 *                      the manual hover handling that keeps a popover open
 *                      while the pointer is over it (so links can be clicked).
 */

function escapeText(value) {
    return value.toString().replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

function apply_popover() {
  // Popover tooltip settings - note we use a manual trigger to support keeping
  // the popup open to allow clicking hyperlinks within the text
  $('.help-popover').popover({
    trigger: "manual",
    placement: "top",
    html: true,
    animation: false,
    container: 'body'
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
