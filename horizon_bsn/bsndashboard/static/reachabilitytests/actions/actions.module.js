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
   * Provides all of the actions for reachability tests.
   */
  angular.module('bsn.bsndashboard.reachabilitytests.actions', [
    'horizon.framework.conf',
  ])
    .run(registerReachabilityTestsActions);

  registerReachabilityTestsActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'bsn.bsndashboard.reachabilitytests.actions.create.service',
    'bsn.bsndashboard.reachabilitytests.actions.run.service',
    'bsn.bsndashboard.reachabilitytests.actions.delete.service',
    'bsn.bsndashboard.reachabilitytests.actions.quick.service',
    'bsn.bsndashboard.reachabilitytests.resourceType'
  ];

  function registerReachabilityTestsActions(
    registry,
    createTestService,
    runTestService,
    deleteTestService,
    quickTestService,
    reachabilityTestsResourceType
  ) {
    var reachabilityTestsResource = registry.getResourceType(reachabilityTestsResourceType);
    reachabilityTestsResource.itemActions
      .append({
        id: 'runTestService',
        service: runTestService,
        template: {
          text: gettext('Run Test')
        }
      })
      .append({
        id: 'deleteTestService',
        service: deleteTestService,
        template: {
          text: gettext('Delete'),
          type: 'delete'
        }
      });

    reachabilityTestsResource.globalActions
      .append({
        id: 'createTestService',
        service: createTestService,
        template: {
          text: gettext('Create Test'),
          type: 'create'
        }
      })
      .append({
        id: 'quickTestService',
        service: quickTestService,
        template: {
          text: gettext('Create Quick Test'),
          type: 'create'
        }
      });

    reachabilityTestsResource.batchActions
      .append({
        id: 'batchDeleteImageAction',
        service: deleteTestService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Tests')
        }
      });
  }

})();
