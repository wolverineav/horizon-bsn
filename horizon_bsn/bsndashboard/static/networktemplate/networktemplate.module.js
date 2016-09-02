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
   * @ngname bsn.bsndashboard.networktemplate
   *
   * @description
   * Provides all of the services and widgets required
   * to support and display network template related content.
   */
  angular
    .module('bsn.bsndashboard.networktemplate', [
      'ngRoute',
      'bsn.bsndashboard.networktemplate.actions',
    ])
    .constant('bsn.bsndashboard.networktemplate.resourceType', 'BSN::Neutron::NetworkTemplate')
    .run(run)
    .config(config);

  run.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'bsn.bsndashboard.networktemplate.basePath',
    'bsn.bsndashboard.networktemplate.resourceType'
  ];

  function run(registry, bsnneutron, basePath, networktemplateResourceType) {
    registry.getResourceType(networktemplateResourceType)
      .setNames(gettext('Network Template'), gettext('Network Templates'))
      .setSummaryTemplateUrl(basePath + 'drawer/drawer.html')
      .setProperty('name', {
        label: gettext('Name')
      })
      .setListFunction(listFunction)
      .tableColumns
      .append({
        id: 'name',
        priority: 1,
        sortDefault: true,
      })


    function listFunction() {
      return bsnneutron.networktemplate_list().success(modifyResponse);

      function modifyResponse(response) {
        var retval = {data: {items: response.items.map(addTrackBy)}};
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
   * 
   * Note: the URL given to $routeProvider must be /bsndashboard/ for the panel that is default. If this panel is
   * changed to not be the default, the route must be updated for both this panel, and the new default panel.
   */
  function config($provide, $windowProvider, $routeProvider) {
    var path = $windowProvider.$get().STATIC_URL + 'networktemplate/';
    $provide.constant('bsn.bsndashboard.networktemplate.basePath', path);

    $routeProvider.when('/bsndashboard/', {
      templateUrl: path + 'panel.html'
    });
  }

})();
