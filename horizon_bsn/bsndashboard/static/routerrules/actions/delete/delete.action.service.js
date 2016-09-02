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
    .module('bsn.bsndashboard.routerrules.actions')
    .factory('bsn.bsndashboard.routerrules.actions.delete.service', deleteRuleService);

  deleteRuleService.$inject = [
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.widgets.modal.deleteModalService',
    'bsn.bsndashboard.routerrules.resourceType',
    '$rootScope',
    'bsn.bsndashboard.routerrules.router',
  ];

  /**
   * @ngdoc factory
   * @name bsn.bsndashboard.routerrules.actions.delete.service

   *
   * @Description
   * Brings up the delete rules confirmation modal dialog.

   * On submit, delete given rules.
   * On cancel, do nothing.
   */
  function deleteRuleService(
    bsnneutron,
    actionResultService,
    deleteModal,
    routerrulesResourceType,
    $scope,
    router
  ) {
    var service = {
      allowed: allowed,
      perform: perform
    };

    return service;

    //////////////

    function perform(items) {
      var rules = angular.isArray(items) ? items : [items];
      rules.map(function(item) {
        item.name = item.priority;
      })

      var context = {};
      context.labels = labelize(rules.length);

      context.deleteEntity = deleteRule;

      // bring up confirm modal
      var outcome = deleteModal.open($scope, rules, context).then(createResult);
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
        actionResult.deleted(routerrulesResourceType, getEntity(item).id);
      });
      deleteModalResult.fail.forEach(function markFailed(item) {
        actionResult.failed(routerrulesResourceType, getEntity(item).id);
      });
      return actionResult.result;
    }

    function deleteRule(id) {
      var newRules = [];
      for (var rule in router.router.router_rules) {
        if (router.router.router_rules[rule].id != id) {
          newRules.push(router.router.router_rules[rule]);
        }
      }
      router.router.router_rules = newRules;

      // remove the rule from the list
      return bsnneutron.router_update(router.router);
    }

    function labelize(count) {
      return {

        title: ngettext(
          'Confirm Delete Rule',
          'Confirm Delete Rules', count),

        message: ngettext(
          'You have selected "%s". A deleted rule is not recoverable.',
          'You have selected "%s". Deleted rules are not recoverable.', count),

        submit: ngettext(
          'Delete Rule',
          'Delete Rules', count),

        success: ngettext(
          'Deleted Rule: %s.',
          'Deleted Rules: %s.', count),

        error: ngettext(
          'Unable to delete rule: %s.',
          'Unable to delete rules: %s.', count)
      };
    }

    function getEntity(result) {
      return result.context;
    }
  }
})();
