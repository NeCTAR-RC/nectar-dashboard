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
    .constant(
      'horizon.dashboard.nectar_dashboard.launch_instance.imagesListCategories',
      [  // nectarImageSelectorController prepends "My Images" to this
        {
          text: 'Nectar official',
          predicate: matchProject('project id'),
        },
        {
          text: 'Contributed',
          predicate: matchProject('project id'),
        },
        {
          text: 'Public',
          predicate: function() { return true; },
        },
      ])
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
    'horizon.dashboard.nectar_dashboard.launch_instance.imagesListCategories',
    'horizon.app.core.openstack-service-api.keystone'
  ];
  function nectarImageSelectorController($scope, categories, keystone) {
    $scope.categories = [{
        text: 'My Images',
        predicate: function() { return false; },
    }].concat(categories);
    $scope.categoryIndex = 0;  // index into $scope.categories
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
