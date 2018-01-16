;(function() {
  'use strict';

  angular
    .module('horizon.dashboard.nectar_dashboard.image_categories', [
      'horizon.app.core.images'
    ])
    .directive('hzResourceTable', hzResourceTable);

  hzResourceTable.$inject = [
    '$compile',
    'horizon.app.core.images.resourceType'
  ];
  function hzResourceTable($compile, imagesResourceType) {
    return {
      restrict: 'E',
      link: function(scope, element, attrs) {
        if(element.attr('resource-type-name') === imagesResourceType) {
          // only match the Images <hz-resource-table>
          var nis = angular.element('<nectar-image-filter></nectar-image-filter>');
          element.before($compile(nis)(scope));
        }
      }
    };
  }
})();
