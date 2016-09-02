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
   * Provides all of the actions for network templates.
   */
  angular.module('bsn.bsndashboard.networktemplate.actions', [
    'horizon.framework.conf',
  ])
    .run(registerNetworkTemplateActions);

  registerNetworkTemplateActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'bsn.bsndashboard.networktemplate.actions.create.service',
    'bsn.bsndashboard.networktemplate.actions.update.service',
    'bsn.bsndashboard.networktemplate.actions.delete.service',
    'bsn.bsndashboard.networktemplate.resourceType'
  ];

  function registerNetworkTemplateActions(
    registry,
    createTemplateService,
    updateTemplateService,
    deleteTemplateService,
    networkTemplateResourceType
  ) {
    var networkTemplateResource = registry.getResourceType(networkTemplateResourceType);
    networkTemplateResource.itemActions
      .append({
        id: 'updateTemplateService',
        service: updateTemplateService,
        template: {
          text: gettext('Edit')
        }
      })
      .append({
        id: 'deleteTemplateService',
        service: deleteTemplateService,
        template: {
          text: gettext('Delete'),
          type: 'delete'
        }
      });

    networkTemplateResource.globalActions
      .append({
        id: 'createTemplateService',
        service: createTemplateService,
        template: {
          text: gettext('Create Template'),
          type: 'create'
        }
      });

    networkTemplateResource.batchActions
      .append({
        id: 'batchDeleteTemplateAction',
        service: deleteTemplateService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Templates')
        }
      });
  }

})();
