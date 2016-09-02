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
    .module('bsn.bsndashboard.networktemplate.actions')
    .factory('bsn.bsndashboard.networktemplate.actions.create.service', createService);

  createService.$inject = [
    'bsn.bsndashboard.networktemplate.resourceType',
    'horizon.app.core.openstack-service-api.bsnneutron',
    'horizon.framework.widgets.toast.service',
    '$modal',
    'horizon.framework.util.actions.action-result.service',
    'horizon.app.core.openstack-service-api.keystone',
  ];

  /**
   * @ngDoc factory
   * @name bsn.bsndashboard.networktemplate.actions.create.service
   * @Description A service to open the network template creation modal.
   */
  function createService(
    resourceType,
    bsnneutron,
    toast,
    $modal,
    actionResultService,
    keystone
  ) {
    var message = {
      success: gettext('Template was successfully created.')
    };

    var service = {
      perform: perform,
      allowed: allowed
    };

    return service;

    //////////////
    /**
     * This function always returns a promise that resolves to true. The upstream Horizon framework requires an 
     * allowed function to exist, but we don't need one for our purposes.
     */
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

    function perform() {
      var localSpec = {
        backdrop: 'static',
        controller: 'CreateNetTemplateController as ctrl',
        templateUrl: '/static/networktemplate/actions/create/createModal.html'
      };

      return $modal.open(localSpec).result.then(function create(result) {
        return submit(result);
      });
    }

    function submit(result) {
      return bsnneutron.networktemplate_create(result).then(onCreateTemplate);
    }

    function onCreateTemplate(response) {
      var newTemplate = response.data;
      toast.add('success', interpolate(message.success, [newTemplate.name]));
      return actionResultService.getActionResult()
        .created(resourceType, newTemplate.id)
        .result;
    }

  } // end of createService
})(); // end of IIFE
