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
   * @description
   * Provides all of the actions for templates.
   */
  angular.module('bsn.bsndashboard.routerrules.actions', [
    'horizon.framework.conf',
  ])
    .run(registerRouterRulesActions);

  registerRouterRulesActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'bsn.bsndashboard.routerrules.actions.create.service',
    'bsn.bsndashboard.routerrules.actions.delete.service',
    'bsn.bsndashboard.routerrules.resourceType'
  ];

  function registerRouterRulesActions(
    registry,
    createRuleService,
    deleteRuleService,
    routerRuleResourceType
  ) {
    var routerRuleResource = registry.getResourceType(routerRuleResourceType);
    routerRuleResource.itemActions
      .append({
        id: 'deleteRuleService',
        service: deleteRuleService,
        template: {
          text: gettext('Delete'),
          type: 'delete'
        }
      });

    routerRuleResource.globalActions
      .append({
        id: 'createRuleService',
        service: createRuleService,
        template: {
          text: gettext('Add Router Policy'),
          type: 'create'
        }
      });
    
    routerRuleResource.batchActions
      .append({
        id: 'batchDeleteRuleService',
        service: deleteRuleService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Rules')
        }
      });
  }
})();
