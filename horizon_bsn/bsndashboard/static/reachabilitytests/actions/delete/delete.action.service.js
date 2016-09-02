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
    .factory('bsn.bsndashboard.reachabilitytests.actions.delete.service', deleteTestService);

  deleteTestService.$inject = [
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.widgets.modal.deleteModalService',
    'bsn.bsndashboard.reachabilitytests.resourceType',
    '$rootScope'
  ];

  /**
   * @ngdoc factory
   * @name bsn.bsndashboard.reachabilitytests.actions.delete.service

   *
   * @Description
   * Brings up the delete tests confirmation modal dialog.

   * On submit, delete given tests.
   * On cancel, do nothing.
   */
  function deleteTestService(
    bsnneutron,
    actionResultService,
    deleteModal,
    reachabilitytestsResourceType,
    $scope
  ) {
    var service = {
      allowed: allowed,
      perform: perform
    };

    return service;

    //////////////

    function perform(items) {
      var tests = angular.isArray(items) ? items : [items];
      var context = {};
      context.labels = labelize(tests.length);

      context.deleteEntity = deleteTest;

      // bring up confirm modal
      var outcome = deleteModal.open($scope, tests, context).then(createResult);
      return outcome;
    }

    function allowed() {
      var promise = new Promise(function (resolve) {
        resolve(true);
      });

      return promise;
    }

    function createResult(deleteModalResult) {
      // To make the result of this action generically useful, reformat the return
      // from the deleteModal into a standard form
      var actionResult = actionResultService.getActionResult();
      deleteModalResult.pass.forEach(function markDeleted(item) {
        actionResult.deleted(reachabilitytestsResourceType, getEntity(item).id);
      });
      deleteModalResult.fail.forEach(function markFailed(item) {
        actionResult.failed(reachabilitytestsResourceType, getEntity(item).id);
      });
      return actionResult.result;
    }

    function deleteTest(id) {
      return bsnneutron.reachabilitytest_delete(id);
    }

    function labelize(count) {
      return {

        title: ngettext(
          'Confirm Delete Test',
          'Confirm Delete Tests', count),

        message: ngettext(
          'You have selected "%s". A deleted test is not recoverable.',
          'You have selected "%s". Deleted tests are not recoverable.', count),

        submit: ngettext(
          'Delete Test',
          'Delete Tests', count),

        success: ngettext(
          'Deleted Test: %s.',
          'Deleted Tests: %s.', count),

        error: ngettext(
          'Unable to delete test: %s.',
          'Unable to delete test: %s.', count)
      };
    }

    function getEntity(result) {
      return result.context;
    }
  }
})();
