;(function() {
  'use strict';

  angular
    .module('horizon.dashboard.nectar_dashboard.launch_instance', [])
    .run(launch_instance);

  // TODO inject $windowProvider and using $windowProvider.$get().STATIC_URL rather than hard-coded '/static'
  launch_instance.$inject = [
    'horizon.dashboard.project.workflow.launch-instance.workflow'
  ];

  function launch_instance(workflow) {
    // ids match strings in launch-instance-workflow.service.js
    workflow.replace('flavor', {
      id: 'nectar-flavor',
      formName: 'launchInstanceNectarFlavorForm',
      templateUrl: '/static/dashboard/nectar_dashboard/launch_instance/flavor/flavor.html',
      helpUrl: '/static/dashboard/nectar_dashboard/launch_instance/flavor/flavor.help.html',
      title: 'Flavor'
    });
  }
})();
