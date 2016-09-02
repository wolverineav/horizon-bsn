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
    .factory('bsn.bsndashboard.reachabilitytests.actions.quick.service', quickService);

  quickService.$inject = [
    'bsn.bsndashboard.reachabilitytests.resourceType',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.widgets.toast.service',
    '$modal',
    'horizon.framework.util.actions.action-result.service',
    '$rootScope'
  ];

  /**
   * @ngDoc factory
   * @name bsn.bsndashboard.reachabilitytests.actions.quick.service
   * @Description A service to open quick test modal.
   */
  function quickService(
    resourceType,
    bsnneutron,
    toast,
    $modal,
    actionResultService,
    $rootScope
  ) {
    var message = {
      success: gettext('Quick Test was successfully created.')
    };

    var model = {};

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

    var quickTest = {};

    function perform() {
      var localSpec = {
        backdrop: 'static',
        controller: 'QuickTestController as ctrl',
        templateUrl: '/static/reachabilitytests/actions/quicktest/quickModal.html'
      };

      /**
       * To execute a quick test, we open the modal to get the parameters (open modal), and then check if a test
       * already exists (get_test). Whether or not it does affects the behavior of create_test. Then, we run the test
       * (run_test). The result of running is passed to the second modal (result_modal), which displays the outcome.
       * Then, the user can continue onto the third modal to save the quicktest as a permanent reachability test
       * (save_test). If this process is completed, the final method is called (onSaveTest).
       */

      return $modal.open(localSpec).result.then(get_test)
        .then(create_test)
        .then(run_test)
        .then(result_modal)
        .then(save_modal)
        .then(save_test)
        .then(onSaveTest);
    }


    function get_test(result) {
      quickTest = result;
      return bsnneutron.reachabilityquicktest_get();
    }
    
    function create_test(result) {
      if (result.data) {
        return bsnneutron.reachabilityquicktest_update(quickTest);
      }
      else {
        return bsnneutron.reachabilityquicktest_create(quickTest);
      }
    }

    function run_test() {
      return bsnneutron.reachabilityquicktest_update({run_test: true});
    }

    function result_modal (result) {
      $rootScope.testResult = result;

      var localSpec = {
        scope: $rootScope,
        backdrop: 'static',
        controller: 'QuickTestResultController as ctrl',
        templateUrl: '/static/reachabilitytests/actions/quicktest/quickResultModal.html'
      };

      return $modal.open(localSpec).result;
    }

    function save_modal () {
      var localSpec = {
        backdrop: 'static',
        controller: 'SaveController as ctrl',
        templateUrl: '/static/reachabilitytests/actions/quicktest/saveModal.html'
      };

      return $modal.open(localSpec).result;
    }

    function save_test (result) {
      quickTest.name = result;
      return bsnneutron.reachabilitytest_create(quickTest);
    }

    function onSaveTest(response) {
      var newTest = response.data;
      toast.add('success', interpolate(message.success, [newTest.name]));
      return actionResultService.getActionResult()
        .created(resourceType, newTest.id)
        .result;
    }

  } // end of quickService
})(); // end of IIFE
