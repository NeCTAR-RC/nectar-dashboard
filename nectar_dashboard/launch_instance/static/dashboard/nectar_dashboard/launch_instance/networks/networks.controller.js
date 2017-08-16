(function () {
  'use strict';

  angular
    .module('horizon.dashboard.nectar_dashboard.launch_instance')
    .controller('NetworksController', NetworksController);

  NetworksController.$inject = [
    '$scope'
  ];

  function NetworksController($scope) {
    var placeholder = {
      'id': '00000000-0000-0000-0000-000000000000',
      'name': 'Classic Provider'
    };
    $scope.$watchCollection(
      function() { return $scope.model.networks; },
      function(networks) {
        if(! networks.some(function(network) { return network.id === placeholder.id; })) {
          // networks does not already contain placeholder
          networks.unshift(placeholder);
        }
      }
    );
    $scope.$watch(
      function() { return $scope.model.initialized; },
      function(initialized) {
        if(initialized) {
          // when model is (re)initialized, select placeholder network
          $scope.model.newInstanceSpec.networks.unshift(placeholder);
        }
      }
    );
  }
})();
