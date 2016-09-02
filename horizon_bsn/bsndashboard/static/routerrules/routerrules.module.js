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
   * @ngname bsn.bsndashboard.routerrules
   *
   * @descriptiont
   * Provides all of the services and widgets required
   * to support and display router policy related content.
   */
  angular
    .module('bsn.bsndashboard.routerrules', [
      'ngRoute',
      'bsn.bsndashboard.routerrules.actions'
    ])
    .constant('bsn.bsndashboard.routerrules.resourceType', 'BSN::Neutron::RouterRules')
    .value('bsn.bsndashboard.routerrules.router', {
      router: {}
    })
    .run(run)
    .config(config);

  run.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'bsn.bsndashboard.routerrules.basePath',
    'bsn.bsndashboard.routerrules.resourceType',
    'bsn.bsndashboard.routerrules.router'
  ];

  function run(registry, bsnneutron, basePath, routerrulesResourceType, router) {
    registry.getResourceType(routerrulesResourceType)
      .setNames(gettext('Router Policy'), gettext('Router Policies'))
      .setSummaryTemplateUrl(basePath + 'drawer/drawer.html')
      .setProperty('priority', {
        label: gettext('Priority')
      })
      .setProperty('sourcecidr', {
        label: gettext('Source CIDR')
      })
      .setProperty('destcidr', {
        label: gettext('Destination CIDR')
      })
      .setProperty('action', {
        label: gettext('Action')
      })
      .setProperty('nexthops', {
        label: gettext('Next Hops')
      })
      .setListFunction(listFunction)
      .tableColumns
      .append({
        id: 'priority',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'source',
        priority: 1,
        sortDefault: true,
      })
     .append({
        id: 'destination',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'action',
        priority: 1,
        sortDefault: true,
      })
      .append({
        id: 'nexthops',
        priority: 1,
        sortDefault: true,
      })
    
    /**
     * This list function is a bit different from the others. Because router rules are not a standalone construct in
     * neutron, we don't have simple API calls to create, read, update, or delete router rules. Instead, we have to 
     * manually modify the router (part of upstream neutron), and do a router patch each time we want to modify a 
     * policy. In order to avoid making unnecessary API calls to router_get, we store the router from router_get on
     * the client side, and do the router updating manually. Then, it's a simple call to router_update each time.
     */
    function listFunction() {
      var result = bsnneutron.router_get().then(modifyResponse);
      return result;

      function modifyResponse(response) {
        router.router = response.data;
        var result = {data: {items: response.data.router_rules.map(addTrackBy)}};
        return result;

        function addTrackBy(template) {
          template.trackBy = template.priority;
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
    var path = $windowProvider.$get().STATIC_URL + 'routerrules/';
    $provide.constant('bsn.bsndashboard.routerrules.basePath', path);

    $routeProvider.when('/bsndashboard/routerrules/', {
      templateUrl: path + 'panel.html'
    });
  }

})();
