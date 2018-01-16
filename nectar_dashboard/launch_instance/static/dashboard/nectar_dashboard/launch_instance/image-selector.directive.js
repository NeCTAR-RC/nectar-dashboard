;(function() {
  'use strict';

  // return predicate function that matches image by owner (project) id
  var matchProject = function(projectId) {
    return function(image) {
      return image.owner === projectId;
    }
  };

  angular
  angular
    .module('horizon.dashboard.nectar_dashboard.launch_instance')
    .directive('nectarImageSelector', nectarImageSelector);

  nectarImageSelector.$inject = [
    '$window'
  ];
  function nectarImageSelector($window) {
    var s = $window.STATIC_URL;
    return {
      templateUrl: s + 'dashboard/nectar_dashboard/launch_instance/image-selector.html',
      controller: nectarImageSelectorController,
      scope: {'model': '='}
    };
  }

  nectarImageSelectorController.$inject = [
    '$scope',
    'horizon.app.core.openstack-service-api.keystone',
    'horizon.app.core.openstack-service-api.settings'
  ];
  function nectarImageSelectorController($scope, keystone, settings) {
    // placeholder: predicate gets set correctly when project id is known
    $scope.categories = [{
        text: 'My Images',
        predicate: function() { return false; }
    }];
    $scope.categoryIndex = 0;  // index into $scope.categories
    settings.getSetting('IMAGES_LIST_FILTER_TENANTS').then(function(fs) {
      // {text, tenant, icon}
      $scope.categories = $scope.categories.concat(fs.map(function(f) {
        return {text: f.text, predicate: matchProject(f.tenant)};
      }));
    });
    $scope.activeImage = null;  // image object currently selected

    // get user's project and update My Images to match
    keystone.getCurrentUserSession().success(function(sess) {
      $scope.categories[0].predicate = matchProject(sess.project_id);
    });

    // view callbacks
    $scope.selectCategory = function(index) {
      $scope.categoryIndex = index;
    };
    $scope.selectImage = function(image) {
      $scope.model.newInstanceSpec.source[0] = image;
    };
    $scope.hasImages = function(index) {
      // this could be cached but $scope.model.images changes
      return $scope.model.images.filter(
        function(image) { return $scope.categories[index].predicate(image); }
      ).length > 0;
    };

    $scope.$watchCollection(
      function() { return $scope.model.newInstanceSpec.source; },
      function(source) {
        if(source.length !== 1) {
          $scope.activeImage = null;
          return;  // panic
        }
        $scope.activeImage = source[0];
      }
    );
  }
})();
