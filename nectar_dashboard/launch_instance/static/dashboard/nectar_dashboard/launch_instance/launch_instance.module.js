;(function() {
  'use strict';

  var onAuthenticated = null;  // gets set in run block
  var getTestURL = function($window, testPath) {
    return ($window.WEBROOT + '/' + testPath).replace(/\/+/g, '/');
  };

  angular
    .module('horizon.dashboard.nectar_dashboard.launch_instance', [
       'horizon.dashboard.project.workflow.launch-instance',
     ])
    .constant(
      // must respond with error status iff user is not logged in
      'horizon.dashboard.nectar_dashboard.launch_instance.loginTestPath',
      '/api/keystone/version')
    .config(addInterceptor)
    .run(testLoggedIn);

  /**
   * Add an interceptor to detect when the user is logged in.
   * This is determined by the response to the test url (see getTestURL).
   * While waiting for such a response, all other responses are stored and then
   * rejected or resolved only after the test url response is received.
   * If the test response is not an error, the user is assumed to be logged
   * in, and onAuthenticated is called.
   *
   * The interceptor must be added in the module configuration block, then the
   * module run block should define onAuthenticated and then make a request to
   * the test url.
   *
   * It is necessary to know whether or not the user is logged in before
   * running any code that assumes the user is logged in, to avoid getting
   * redirected to /auth/logout (and if the login page runs any code that
   * assumes the user is logged in, getting stuck in a redirect loop).
   *
   * launch-instance workflow has steps with requiredServiceTypes,
   * which causes horizon.app.core.workflow.decorator to call serviceCatalog.ifTypeEnabled,
   * which calls horizon.app.core.openstack-service-api.keystone getCurrentUserSession,
   * which calls horizon.framework.util.http.service to GET /api/keystone/user-session
   * using $http, which has a "Global http error handler" interceptor defined in
   * horizon.framework which redirects to /auth/logout. Therefore any code (i.e.
   * the launch_instance function) which depends on the launch-instance
   * workflow should not be called unless the user is logged in.
   *
   * There should be a better way to achieve this.
   */
  addInterceptor.$inject = [
    '$httpProvider',
    '$windowProvider',
    'horizon.dashboard.nectar_dashboard.launch_instance.loginTestPath',
  ];
  function addInterceptor($httpProvider, $windowProvider, loginTestPath) {
    var testURL = getTestURL($windowProvider.$get(), loginTestPath);
    var catch401 = function($q) {
      var enabled = true;
      var catches = [];  // list of functions, each of which resolves or rejects a response
      var catcher = function(isError) {
        return function(r) {
          if(enabled) {
            if(r.config.url === testURL) {
              catches.forEach(function(c) { c(); });
              enabled = false;
              if(!isError) {
                onAuthenticated(); // user is logged in: run code
              }
              return null;  // FIXME is it better to return $q.defer().promise which will never be resolved?
            } else {
              var deferred = $q.defer();
              catches.push(function() { (isError ? deferred.reject : deferred.resolve)(r); });
              return deferred.promise;
            }
          } else {
            return (isError ? $q.reject(r) : $q.resolve(r));
          }
        };
      };
      return {
        response: catcher(false),
        responseError: catcher(true)
      };
    };
    catch401.$inject = ['$q'];
    $httpProvider.interceptors.push(catch401);
  }

  testLoggedIn.$inject = [
    '$http',
    '$window',
    '$injector',
    'horizon.dashboard.nectar_dashboard.launch_instance.loginTestPath',
  ];
  function testLoggedIn($http, $window, $injector, loginTestPath) {
    onAuthenticated = function() {
      $injector.invoke(launch_instance);
    };
    $http({
      method: 'GET',
      url: getTestURL($window, loginTestPath),
    });
  }

  launch_instance.$inject = [
    '$window',
    'horizon.dashboard.project.workflow.launch-instance.workflow',
  ];

  function launch_instance($window, workflow) {
    var s = $window.STATIC_URL;

    // ids match strings in launch-instance-workflow.service.js
    workflow.replace('flavor', {
      id: 'nectar-flavor',
      formName: 'launchInstanceNectarFlavorForm',
      templateUrl: s + 'dashboard/nectar_dashboard/launch_instance/flavor/flavor.html',
      helpUrl: s + 'dashboard/nectar_dashboard/launch_instance/flavor/flavor.help.html',
      title: 'Flavor'
    });
    workflow.after('details', {
      id: 'nectar-az',
      formName: 'launchInstanceNectarAvailabilityZoneForm',
      templateUrl: s + 'dashboard/nectar_dashboard/launch_instance/az/az.html',
      helpUrl: s + 'dashboard/nectar_dashboard/launch_instance/az/az.help.html',
      title: 'Availability Zone'
    });
    workflow.addController('NetworksController');
  }
})();
