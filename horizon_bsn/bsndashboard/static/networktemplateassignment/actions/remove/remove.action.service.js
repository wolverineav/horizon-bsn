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
    .module('bsn.bsndashboard.networktemplateassignment.actions')
    .factory('bsn.bsndashboard.networktemplateassignment.actions.remove.service', deleteTemplateService);

  deleteTemplateService.$inject = [
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.app.core.openstack-service-api.keystone',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.framework.widgets.modal.deleteModalService',
    'horizon.framework.widgets.toast.service',
    'bsn.bsndashboard.networktemplateassignment.resourceType',
    '$rootScope'
  ];

  /**
   * @ngdoc factory
   * @name bsn.bsndashboard.networktemplateassignment.actions.delete.service

   *
   * @Description
   * Brings up the delete template assignment confirmation modal dialog.

   * On submit, delete given templates.
   * On cancel, do nothing.
   */
  function deleteTemplateService(
    bsnneutron,
    keystone,
    actionResultService,
    gettext,
    deleteModal,
    toast,
    networktemplateassignmentResourceType,
    $scope
  ) {
    var service = {
      allowed: allowed,
      perform: perform
    };

    return service;

    //////////////

    function perform(template) {
      var context = {};
      context.labels = labelize(1);

      context.deleteEntity = deleteTemplate;

      // bring up confirm modal
      var outcome = deleteModal.open($scope, [template], context).then(createResult);
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
        actionResult.deleted(networktemplateassignmentResourceType, getEntity(item).stack_id);
      });
      deleteModalResult.fail.forEach(function markFailed(item) {
        actionResult.failed(networktemplateassignmentResourceType, getEntity(item).stack_id);
      });
      return actionResult.result;
    }

    function deleteTemplate() {
      // delete heat stack
      return bsnneutron.networktemplateassignment_list().then(function(nettemplate_response) {
        // use stack_id in response to delete the stack
        return bsnneutron.heatstack_delete(nettemplate_response.data.items[0].stack_id);
      });
    }

    function labelize(count) {
      return {

        title: ngettext(
          'Confirm Remove Template',
          'Confirm Remove Templates', count),

        message: ngettext(
          'You have selected "%s". A removed template is not recoverable.',
          'You have selected "%s". Removed templates are not recoverable.', count),

        submit: ngettext(
          'Remove Template',
          'Remove Templates', count),

        success: ngettext(
          'Remove in progress: %s.',
          'Remove in progress: %s.', count),

        error: ngettext(
          'Unable to remove template: %s.',
          'Unable to remove templates: %s.', count)
      };
    }


    function getEntity(result) {
      return result.context;
    }
  }
})();
