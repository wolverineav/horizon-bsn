/**
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use self file except in compliance with the License. You may obtain
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
    .factory('bsn.bsndashboard.reachabilitytests.actions.run.service', runTestService);

  runTestService.$inject = [
    'bsn.bsndashboard.reachabilitytests.resourceType',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.widgets.toast.service'
  ];

  /**
   * @ngdoc factory
   * @name bsn.bsndashboard.reachabilitytests.actions.run.service

   *
   * @Description
   * Brings up the run tests confirmation modal dialog.

   * On submit, run given tests.
   * On cancel, do nothing.
   */
  function runTestService(
    resourceType,
    bsnneutron,
    actionResultService,
    toast
  ) {
    var service = {
      allowed: allowed,
      perform: perform
    };

    var message = {
      success: gettext('Test was successfully run.')
    };

    return service;

    //////////////

    function perform(test) {
      var outcome = bsnneutron.reachabilitytest_run(test.id).then(onRunTest);
      return outcome;
    }

    function allowed() {
      var promise = new Promise(function (resolve) {
        resolve(true);
      });

      return promise;
    }

    function onRunTest(response) {
      var test = response.data;
      toast.add('success', interpolate(message.success, [test.name]));
      return actionResultService.getActionResult()
        .updated(resourceType, test.id)
        .result;
    }
  }
})();
