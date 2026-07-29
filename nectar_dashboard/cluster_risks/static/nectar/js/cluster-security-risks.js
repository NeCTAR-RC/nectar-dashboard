/**
 * Adds a security risk icon to the magnum-ui clusters table, next to the
 * cluster name, mirroring the instances table risk column.
 *
 * The risk data comes from the varroa service: nectar_dashboard.overrides
 * replaces the magnum-ui clusters REST view with one that attaches a
 * security_risks list to each cluster. When magnum-ui is not deployed
 * this module registers a column on an unused resource type, which is
 * harmless.
 */
(function() {
  'use strict';

  angular
    .module('nectar.cluster-security-risks', [])
    .run(run);

  run.$inject = ['horizon.framework.conf.resource-type-registry.service'];

  function run(registry) {
    // target="_self" forces a full page load: the security panel is a
    // Django page, and without it AngularJS ($locationProvider.html5Mode)
    // swallows the click because the path is not an Angular route.
    var securityRisksTemplate =
      '<a ng-if="item.security_risks.length" ' +
      'href="/project/security/#{$ item.id $}" target="_self" ' +
      'title="' +
      gettext('This cluster has security risks. Click to learn more.') +
      '" class="fa fa-exclamation-circle text-danger ' +
      'text-decoration-none"></a>';

    // title is a single space: an empty string would fall back to a
    // label derived from the column id, and like the instances table
    // this icon column has no header.
    registry.getResourceType('OS::Magnum::Cluster')
      .tableColumns
      .after('name', {
        id: 'security_risks',
        title: ' ',
        priority: 1,
        template: securityRisksTemplate
      });
  }
})();
