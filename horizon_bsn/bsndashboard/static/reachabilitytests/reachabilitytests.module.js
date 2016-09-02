/**
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

(function() {
  'use strict';
  /**
   * @ngdoc overview
   * @ngname bsn.bsndashboard.reachabilitytests
   *
   * @description
   * Provides all of the services and widgets required
   * to support and display reachability test related content.
   */
  angular
    .module('bsn.bsndashboard.reachabilitytests', [
      'ngRoute',
      'bsn.bsndashboard.reachabilitytests.actions'
    ])
    .constant('bsn.bsndashboard.reachabilitytests.resourceType', 'BSN::Neutron::ReachabilityTests')
    .run(run)
    .config(config);

  run.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'bsn.bsndashboard.reachabilitytests.basePath',
    'bsn.bsndashboard.reachabilitytests.resourceType'
  ];

  /**
   * Getting the table to update the test_time and test_result after running is difficult. Instead, these are put in
   * the drawer as a workaround.
   */
  function run(registry, bsnneutron, basePath, reachabilitytestsResourceType) {
    registry.getResourceType(reachabilitytestsResourceType)
      .setNames(gettext('Reachability Tests'), gettext('Reachability Tests'))
      .setSummaryTemplateUrl(basePath + 'drawer/drawer.html')
      .setProperty('name', {
        label: gettext('Name')
      })
      .setProperty('src_tenant_name', {
        label: gettext('Source Tenant')
      })
      .setProperty('src_segment_name', {
        label: gettext('Source Segment')
      })
      .setProperty('src_ip', {
        label: gettext('Source IP')
      })
      .setProperty('dst_ip', {
        label: gettext('Destination IP')
      })
      .setProperty('test_time', {
        label: gettext('Last Run')
      })
      .setProperty('test_result', {
        label: gettext('Status')
      })
      .setProperty('expected_result', {
        label: gettext('Expected Result')
      })
      .setListFunction(listFunction)
      .tableColumns
      .append({
        id: 'name',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'src_tenant_name',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'src_segment_name',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'src_ip',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'dst_ip',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'expected_result',
        priority: 1,
        sortDefault: true,
      });

    function listFunction() {
      return bsnneutron.reachabilitytest_list().then(modifyResponse);

      function modifyResponse(response) {
        return {data: {items: response.data.items.map(addTrackBy)}};

        function addTrackBy(test) {
          test.trackBy = test.name;
          return test;
        }
      }
    }
  }

  config.$inject = [
    '$provide',
    '$windowProvider',
    '$routeProvider'
  ];

  /**
   * @name config
   * @param {Object} $provide
   * @param {Object} $windowProvider
   * @param {Object} $routeProvider
   * @description Routes used by this module.
   * @returns {undefined} Returns nothing
   */
  function config($provide, $windowProvider, $routeProvider) {
    var path = $windowProvider.$get().STATIC_URL + 'reachabilitytests/';
    $provide.constant('bsn.bsndashboard.reachabilitytests.basePath', path);

    $routeProvider.when('/bsndashboard/reachabilitytests/', {
      templateUrl: path + 'panel.html'
    });
  }

})();
