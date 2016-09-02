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
    .module('bsn.bsndashboard.networktemplate.actions')
    .factory('bsn.bsndashboard.networktemplate.actions.delete.service', deleteTemplateService);

  deleteTemplateService.$inject = [
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.widgets.modal.deleteModalService',
    'bsn.bsndashboard.networktemplate.resourceType',
    '$rootScope',
    'horizon.app.core.openstack-service-api.keystone'
  ];

  /**
   * @ngdoc factory
   * @name bsn.bsndashboard.networktemplate.actions.delete.service

   *
   * @Description
   * Brings up the delete templates confirmation modal dialog.

   * On submit, delete given templates.
   * On cancel, do nothing.
   */
  function deleteTemplateService(
    bsnneutron,
    actionResultService,
    deleteModal,
    networktemplateResourceType,
    $scope,
    keystone
  ) {
    var service = {
      allowed: allowed,
      perform: perform
    };

    return service;

    //////////////

    function perform(items) {
      var templates = angular.isArray(items) ? items : [items];
      var context = {};
      context.labels = labelize(templates.length);

      context.deleteEntity = deleteTemplate;

      // bring up confirm modal
      var outcome = deleteModal.open($scope, templates, context).then(createResult);
      return outcome;
    }

    function allowed() {
      return keystone.getCurrentUserSession()
        .then(function (result) {
          if (result.data.is_superuser) {
            var promise = new Promise(function (resolve) {
              resolve(true);
            });
            return promise;
          }
          else {
            var promise = new Promise(function (resolve, reject) {
              reject(false);
            });
            return promise;
          }
        });
    }

    function createResult(deleteModalResult) {
      // To make the result of this action generically useful, reformat the return
      // from the deleteModal into a standard form
      var actionResult = actionResultService.getActionResult();
      deleteModalResult.pass.forEach(function markDeleted(item) {
        actionResult.deleted(networktemplateResourceType, getEntity(item).id);
      });
      deleteModalResult.fail.forEach(function markFailed(item) {
        actionResult.failed(networktemplateResourceType, getEntity(item).id);
      });
      return actionResult.result;
    }

    function deleteTemplate(id) {
      return bsnneutron.networktemplate_delete(id);
    }

    function labelize(count) {
      return {

        title: ngettext(
          'Confirm Delete Template',
          'Confirm Delete Templates', count),

        message: ngettext(
          'You have selected "%s". A deleted template is not recoverable.',
          'You have selected "%s". Deleted templates are not recoverable.', count),

        submit: ngettext(
          'Delete Template',
          'Delete Templates', count),

        success: ngettext(
          'Deleted Template: %s.',
          'Deleted Templates: %s.', count),

        error: ngettext(
          'Unable to delete template: %s.',
          'Unable to delete templates: %s.', count)
      };
    }

    function getEntity(result) {
      return result.context;
    }
  }
})();
