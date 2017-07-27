(function () {
  'use strict';

  angular
    .module('horizon.dashboard.nectar_dashboard.launch_instance')
    .filter('shouldShowAvailabilityZone', AvailabilityZoneFilter)
    .controller('AvailabilityZoneController', AvailabilityZoneController);

  AvailabilityZoneController.$inject = [
    '$scope'
  ];

  function AvailabilityZoneController($scope) {
    $scope.showAll = false;  // not sure if there's a better place/way to initialise this value
  }

  function AvailabilityZoneFilter() {
    return function(arr, showAll, currentValue) {
      return arr.filter(function(az) {
        return showAll || az.value.indexOf('-') === -1 || az.value === currentValue;
      });
    };
  }
})();
