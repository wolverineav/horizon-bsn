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
   * @ngname bsn.bsndashboard.networktemplateassignment
   *
   * @description
   * Provides all of the services and widgets required
   * to support and display network template assignmen related content.
   */
  angular
    .module('bsn.bsndashboard.networktemplateassignment', [
      'ngRoute',
      'bsn.bsndashboard.networktemplateassignment.actions',
    ])
    .constant('bsn.bsndashboard.networktemplateassignment.resourceType', 'BSN::Neutron::NetworkTemplateAssignment')
    .run(run)
    .config(config);

  run.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'bsn.bsndashboard.networktemplateassignment.basePath',
    'bsn.bsndashboard.networktemplateassignment.resourceType'
  ];

  function run(registry, bsnneutron, basePath, networktemplateassignmentResourceType) {
    registry.getResourceType(networktemplateassignmentResourceType)
      .setNames(gettext('Network Template Assignment'), gettext('Network Template Assignment'))
      .setSummaryTemplateUrl(basePath + 'drawer/drawer.html')
      .setProperty('name', {
        label: gettext('Template Name')
      })
      .setProperty('heat_stack_name', {
        label: gettext('Heat Stack Name')
      })
      .setProperty('description', {
        label: gettext('Description')
      })
      .setProperty('resources', {
        label: gettext('Resources')
      })
      .setProperty('status', {
        label: gettext('Status')
      })
      .setListFunction(listFunction)
      .tableColumns
      .append({
        id: 'name',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'heat_stack_name',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'description',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'status',
        priority: 1,
        sortDefault: true,
      })


    function listFunction() {
      return bsnneutron.networktemplateassignment_list().success(modifyResponse);

      function modifyResponse(response) {
        var retval =  {data: {items: response.items.map(addTrackBy)}};
        return retval;

        function addTrackBy(template) {
          template.trackBy = template.name;
          return template;
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
    var path = $windowProvider.$get().STATIC_URL + 'networktemplateassignment/';
    $provide.constant('bsn.bsndashboard.networktemplateassignment.basePath', path);

    $routeProvider.when('/bsndashboard/networktemplateassignment/', {
      templateUrl: path + 'panel.html'
    });
  }

})();
