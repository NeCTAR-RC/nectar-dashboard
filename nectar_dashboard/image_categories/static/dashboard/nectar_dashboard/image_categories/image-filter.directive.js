;(function() {
  'use strict';

  /**
   * 1. define IMAGES_LIST_FILTER_TENANTS and IMAGES_LIST_FILTER_PROPERTIES in *settings.py
   *    (see horizon/doc/source/topics/settings.rst)
   * 2. add 'IMAGES_LIST_FILTER_TENANTS' and 'IMAGES_LIST_FILTER_PROPERTIES'
   *    to REST_API_ADDITIONAL_SETTINGS in local_settings.py
   * 3. define horizon.dashboard.nectar_dashboard.image_categories.subfilterProperty
   *    below (may require adding new field to image metadata)
   *    [this should probably actually come from horizon settings]
   *
   * If step 2 is skipped, this code gets "undefined" from the settings api call;
   * if step 1 is skipped, this code gets "null" from the settings api call.
   */

  angular
    .module('horizon.dashboard.nectar_dashboard.image_categories')
    .constant('horizon.dashboard.nectar_dashboard.image_categories.subfilterProperty', 'properties.description')  // property of image object, which describes its operating system
    .directive('nectarImageFilter', imageFilter);

  imageFilter.$inject = [
    '$window'
  ];
  function imageFilter($window) {
    var s = $window.STATIC_URL;
    return {
      restrict: 'E',
      templateUrl: s + 'dashboard/nectar_dashboard/image_categories/image-filter.html',
      controller: imageFilterController
    };
  }

  // returns a function which maps prop to a (nested) property of its input
  // or undefined if the property does not exist
  // e.g. subfilterFunction('x.y')({x: {y: 'treasure'}}) === 'treasure'
  var subfilterFunction = function(prop) {
    return function(o) {
      var props = prop.split('.');
      for(var i = 0; i < props.length - 1; i++) {
        o = o[props[i]];
        if(o === undefined) return undefined;
      }
      return o[props[props.length - 1]];
    };
  }

  imageFilterController.$inject = [
    '$scope',
    '$filter',
    'horizon.dashboard.nectar_dashboard.image_categories.subfilterProperty',
    'horizon.app.core.openstack-service-api.settings',
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.app.core.images.resourceType',
    'horizon.framework.widgets.magic-search.events',
    'horizon.app.core.openstack-service-api.keystone'
  ];
  function imageFilterController($scope, $filter, subfilterProperty, settings, registry, resourceTypeName, magicSearchEvents, keystone) {
    registry.getResourceType(resourceTypeName).list().then(function(data) {
      var ossAll = data.data.items.map(subfilterFunction(subfilterProperty));
      console.log('ossAll', ossAll);
      var oss = ossAll.filter(function(x, i, self) { return self.indexOf(x) === i && x !== undefined; });
      $scope.subfilters = $scope.subfilters.concat(oss.map(function(os) {
        return {
          text: os,
          query: subfilterProperty + '=' + os
        };
      }));
    });

    // filters and subfilters have two properties:
    //  text   which appears in the widget
    //  query  which is used to restrict what is shown
    $scope.filters = [{
      text: 'My Images',
      query: ''
    }];
    $scope.subfilters = [{
      text: 'All',
      query: ''
    }];
    $scope.index = -1;
    $scope.subIndex = -1;
    $scope.image = null;

    settings.getSetting('IMAGES_LIST_FILTER_TENANTS').then(function(fs) {
      // {text, tenant, icon}
      $scope.filters = $scope.filters.concat(fs.map(function(f) {
        return {text: f.text, owner:f.tenant, query: 'owner=' + f.tenant};
      }));
    });

    var searchQuery = '';
    $scope.$on(magicSearchEvents.SEARCH_UPDATED, function(event, query, ignore) {
      if(ignore) return;
      // ideally there would be some way of stopping this event from being
      // handled elsewhere (in particular, the watcher in
      // st-magic-search.directive.js which calls angular's smart-table.js
      // search, which makes horizon.framework.widgets.table call listResources
      // for the images, making a xhr request, then doing it all over again
      // when this function broadcasts the same event with a slightly different
      // search query) but this does not seem easy...

      // watch for any changes to search query, so we can include all current
      // search params when we re-broadcast SEARCH_UPDATED events
      searchQuery = query;
      updateSearch(query);
    });

    var updateSearch = function() {
      var q = searchQuery
            + ($scope.index >= 0 ? '&' + $scope.filters[$scope.index].query : '')
            + ($scope.subIndex >= 0 ? '&' + $scope.subfilters[$scope.subIndex].query : '');
      $scope.$broadcast(magicSearchEvents.SEARCH_UPDATED, q, true);
    };

    // FIXME calling clearSearch also will clear whatever gets set by my widget
    // (so widget should watch for clearSearch then update search afterwards)

    // view callbacks
    $scope.filterOn = function(index) {
      $scope.index = index;
      updateSearch();
    };
    $scope.subfilterOn = function(index) {
      $scope.subIndex = index;
      updateSearch();
    };
  }
})();
