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

  angular
    .module('bsn.bsndashboard.reachabilitytests.actions')
    .factory('bsn.bsndashboard.reachabilitytests.actions.create.service', createService);

  createService.$inject = [
    'bsn.bsndashboard.reachabilitytests.resourceType',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.widgets.toast.service',
    '$modal',
    'horizon.framework.util.actions.action-result.service',
  ];

  /**
   * @ngDoc factory
   * @name bsn.bsndashboard.reachabilitytests.actions.create.service
   * @Description A service to open reachability test create modal.
   */
  function createService(
    resourceType,
    bsnneutron,
    toast,
    $modal,
    actionResultService
  ) {
    var message = {
      success: gettext('Test was successfully created.')
    };

    var service = {
      perform: perform,
      allowed: allowed
    };

    return service;

    //////////////
    function allowed() {
      var promise = new Promise(function (resolve) {
        resolve(true);
      });

      return promise;
    }

    function perform() {
      var localSpec = {
        backdrop: 'static',
        controller: 'CreateReachTestController as ctrl',
        templateUrl: '/static/reachabilitytests/actions/create/createModal.html'
      };

      return $modal.open(localSpec).result.then(function (result) {
        return submit(result);
      });
    }

    function submit(result) {
      return bsnneutron.reachabilitytest_create(result).then(onCreateTest);
    }

    function onCreateTest(response) {
      var newTest = response.data;
      toast.add('success', interpolate(message.success, [newTest.name]));
      return actionResultService.getActionResult()
        .created(resourceType, newTest.id)
        .result;
    }

  } // end of createService
})(); // end of IIFE
