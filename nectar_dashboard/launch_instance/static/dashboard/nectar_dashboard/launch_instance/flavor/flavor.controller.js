(function () {
  'use strict';

  angular
    .module('horizon.dashboard.nectar_dashboard.launch_instance')
    .controller('FlavorController', FlavorController);

  FlavorController.$inject = [
    '$scope',
    'horizon.framework.widgets.wizard.events',
    'horizon.framework.widgets.charts.donutChartSettings',
    'horizon.framework.widgets.charts.quotaChartDefaults'
  ];

  function FlavorController($scope, wizardEvents, donutChartSettings, quotaChartDefaults) {
    var ctrl = this;
    ctrl.defaultIfUndefined = defaultIfUndefined;
    ctrl.getChartData = getChartData;
    ctrl.redraw = redraw;

    // donut chart
    ctrl.chartSettings = donutChartSettings;

    ctrl.instancesChartData = undefined;
    ctrl.vcpusChartData = undefined;
    ctrl.ramChartData = undefined;

    // TODO remove watchers when controller is destroyed
    // see details.controller.js $scope.$on('$destroy', ...)

    $scope.$watchCollection(
      function() { return $scope.model.novaLimits; },
      redraw
    );

    $scope.$watch(
      function() { return $scope.model.newInstanceSpec.instance_count; },
      redraw
    );

    $scope.$watch(
      function() { return $scope.model.newInstanceSpec.flavor; },
      redraw
    );

    function redraw() {
      var isValid = false;  // flavor * instance_count <= quota limits
      var spec = $scope.model.newInstanceSpec;
      if(
        $scope.model.novaLimits === undefined ||
        spec.instance_count === undefined ||
        spec.flavor === undefined ||
        spec.flavor === null
      ) {
        ctrl.instancesChartData = undefined;
        ctrl.vcpusChartData = undefined;
        ctrl.ramChartData = undefined;
      } else {
        ctrl.instancesChartData = ctrl.getChartData(
          gettext('Total Instances'),
          spec.instance_count,
          $scope.model.novaLimits.totalInstancesUsed,
          $scope.model.novaLimits.maxTotalInstances
        );
        ctrl.vcpusChartData = ctrl.getChartData(
          gettext('Total VCPUs'),
          spec.instance_count * spec.flavor.vcpus,
          $scope.model.novaLimits.totalCoresUsed,
          $scope.model.novaLimits.maxTotalCores
        );
        ctrl.ramChartData = ctrl.getChartData(
          gettext('Total RAM'),
          spec.instance_count * spec.flavor.ram,
          $scope.model.novaLimits.totalRAMUsed,
          $scope.model.novaLimits.maxTotalRAMSize
        );

        // mark selected flavor as invalid if any quota would be exceeded
        isValid = !(
          ctrl.instancesChartData.overMax ||
          ctrl.vcpusChartData.overMax ||
          ctrl.ramChartData.overMax
        );
      }

      // update form validity
      $scope.launchInstanceNectarFlavorForm.$setValidity('flavor', isValid);
    };

    // this is the same as in LaunchInstanceFlavorController;
    // it would be nicer if the code existed in a reusable service instead,
    // but as long as it's internal to LaunchInstanceFlavorController
    // I can't see a robust way of sharing the code
    function defaultIfUndefined(value, defaultValue) { return angular.isUndefined(value) ? defaultValue : value; };
    function getChartData(title, added, totalUsed, maxAllowed) {
      var used = ctrl.defaultIfUndefined(totalUsed, 0);
      var allowed = ctrl.defaultIfUndefined(maxAllowed, 1);
      var quotaCalc = Math.round((used + added) / allowed * 100);
      var overMax = quotaCalc > 100;

      var usageData = {
        label: quotaChartDefaults.usageLabel,
        value: used,
        colorClass: quotaChartDefaults.usageColorClass
      };
      var addedData = {
        label: quotaChartDefaults.addedLabel,
        value: added,
        colorClass: quotaChartDefaults.addedColorClass
      };
      var remainingData = {
        label: quotaChartDefaults.remainingLabel,
        value: Math.max(0, allowed - used - added),
        colorClass: quotaChartDefaults.remainingColorClass
      };
      var chartData = {
        title: title,
        maxLimit: allowed,
        label: quotaCalc + '%',
        overMax: overMax,
        data:  [usageData, addedData, remainingData]
      };

      return chartData;
    };
  }

})();
