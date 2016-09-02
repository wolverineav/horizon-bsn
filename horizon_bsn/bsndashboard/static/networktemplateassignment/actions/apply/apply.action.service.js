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
    .module('bsn.bsndashboard.networktemplateassignment.actions')
    .factory('bsn.bsndashboard.networktemplateassignemnt.actions.apply.service', applyService);

  applyService.$inject = [
    'bsn.bsndashboard.networktemplateassignment.resourceType',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.widgets.toast.service',
    '$modal',
    'horizon.framework.util.actions.action-result.service',
    '$rootScope'
  ];

  /**
   * @ngDoc factory
   * @name bsn.bsndashboard.networktemplateassignemnt.actions.apply.service
   * @Description A service to open the apply template modal.
   */
  function applyService(
    resourceType,
    bsnneutron,
    toast,
    $modal,
    actionResultService,
    $rootScope
  ) {
    var message = {
      success: gettext('Template application in progress.')
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
    
    var stack_create_response = {};
    var template = {};
    var parameters = {};

    function perform() {

      return bsnneutron.networktemplateassignment_list()
        .then(function (result) {
          if (result.data.items) {
            // there is already a template applied, cannot apply another
            var localSpec = {
              backdrop: 'static',
              templateUrl: '/static/networktemplateassignment/actions/apply/denyModal.html'
            }
            $modal.open(localSpec).result;
            return;
          }
          else {
            // there is not template yet, we can apply one
            return apply();
          }
        })
    }

    /**
     * To apply a network template, we open the selection modal (modal.open). Once the user has selected a network
     * template to apply, we get the fields required for the network template (validateTemplte). Once the input fields
     * are returned, we can open the second modal to fill in the arguments (applyTemplate). Then, we can create the
     * assignment (createNetTemplateAssign), create the heat stack (createHeatStack), and update the assignment
     * (updateNetTemplateAssign). When this is done, we return with onApplyTemplate. The controller is then responsible
     * for querying Heat for the status of the heat stack creation, and then update the table.
     */

    /**
     * TODO: Improvement to apply template modal.
     * We can use the new workflow framekwork in this commit: https://review.openstack.org/#/c/332745/ to improve
     * the modal that selects the network template. Currently, we only select the name of the network template,
     * but it would be helpful for users to be able to see the body associated with the template selected (in similar
     * fashion to the launch instance modal of the instances panel).
     *
     */

    function apply() {
      var localSpec = {
        backdrop: 'static',
        controller: 'SelectNetTemplateController as ctrl',
        templateUrl: '/static/networktemplateassignment/actions/apply/selectModal.html'
      };

      return $modal.open(localSpec).result
        .then(validateTemplate)
        .then(applyTemplate)
        .then(createNetTemplateAssign)
        .then(createHeatStack)
        .then(updateNetTemplateAssign)
        .then(onApplyTemplate);
    }

    function validateTemplate(selectResult) {
      var result = JSON.parse(selectResult.template);
      template = result;
      return bsnneutron.template_validate(result);
    }

    function applyTemplate(validateResult) {
      $rootScope.properties = validateResult.data;
      var localSpec = {
        backdrop: 'static',
        controller: 'SelectNetTemplateController as ctrl',
        templateUrl: '/static/networktemplateassignment/actions/apply/applyModal.html',
        scope: $rootScope
      };
      return $modal.open(localSpec).result
    }

    function createNetTemplateAssign(params){
      parameters = params;

      var assignment = {
        template_id: template.id,
        stack_id: 'PENDING'
      };
      return bsnneutron.networktemplateassignment_create(assignment);
    }

    function createHeatStack() {
      var args = {
        stack_name: template.name,
        parameters: parameters,
        template: template.body
      };

      return bsnneutron.heatstack_create(args);
    }

    function updateNetTemplateAssign(response) {
      stack_create_response = response;
      return bsnneutron.networktemplateassignment_update({'stack_id': response.data.stack.id});
    }

    function onApplyTemplate() {
      var newStack = stack_create_response.data;
      toast.add('success', interpolate(message.success, [newStack.stack.id]));
      return actionResultService.getActionResult()
        .created(resourceType, newStack.stack.id)
        .result;
    }

  } // end of applyService
})(); // end of IIFE
