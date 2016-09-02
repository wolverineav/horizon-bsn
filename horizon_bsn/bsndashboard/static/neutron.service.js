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
(function () {
  'use strict';

  angular
    .module('horizon.app.core.openstack-service-api')
    .factory('horizon.app.core.openstack-service-api.bsnneutron', neutronAPI);

  neutronAPI.$inject = [
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service'
  ];

  /**
   * @ngdoc service
   * @name neutronAPI
   * @param {Object} apiService
   * @param {Object} toastService
   * @description Provides access to Neutron APIs.
   * @returns {Object} The service
   */
  function neutronAPI(apiService, toastService) {
    var service = {
      reachabilitytest_create: reachabilitytest_create,
      reachabilitytest_list: reachabilitytest_list,
      reachabilitytest_run: reachabilitytest_run,
      reachabilitytest_delete: reachabilitytest_delete,

      networktemplate_create: networktemplate_create,
      networktemplate_list: networktemplate_list,
      networktemplate_get: networktemplate_get,
      networktemplate_update: networktemplate_update,
      networktemplate_delete: networktemplate_delete,

      heatstack_delete: heatstack_delete,
      heatstack_create: heatstack_create,
      check_status: check_status,
      template_validate: template_validate,
      networktemplateassignment_create: networktemplateassignment_create,
      networktemplateassignment_list: networktemplateassignment_list,
      networktemplateassignment_update: networktemplateassignment_update,
      networktemplateassignment_delete: networktemplateassignment_delete,
      
      reachabilityquicktest_create: reachabilityquicktest_create,
      reachabilityquicktest_get: reachabilityquicktest_get,
      reachabilityquicktest_update: reachabilityquicktest_update,

      router_get: router_get,
      router_update: router_update
    };

    return service;

    /////////////

    // Neutron Services


    /**
     * //////////////////////////////////////////
     * REACHABILITY TESTS
     * //////////////////////////////////////////
     */
    /**
     * @name reachabilitytest_create
     * @param {Object} test - The test
     * @description Create a reachability test.
     *
     * @returns {Object} The result of the creation call.
     */
    function reachabilitytest_create(test) {
      return apiService.post('api/neutron/reachabilitytests/', test)
        .error(function () {
          toastService.add('error', gettext('Error creating reachability test'));
        });
    }

    /**
     * @name reachabilitytest_list
     * @description Get the list of reachability tests.
     *
     * @returns {Object} An object with property "items." Each item is a test.
     */
    function reachabilitytest_list() {
      return apiService.get('api/neutron/reachabilitytests/')
        .error(function () {
          toastService.add('error', gettext('Error getting reachability tests'));
        });
    }

    /**
     * @name reachabilitytest_run
     * @description Run a reachability test.
     *
     * @returns {Object} The result of running the reachability test.
     */
    function reachabilitytest_run(id) {
      return apiService.patch('api/neutron/reachabilitytests/' + id + '/')
        .error(function () {
          toastService.add('error', gettext('Error running reachability tests'));
        });
    }

    /**
     * @name reachabilitytest_delete
     * @description Delete a reachability test.
     *
     * @returns {Object} An object with property "items." Each item is a test.
     */
    function reachabilitytest_delete(id) {
      return apiService.delete('api/neutron/reachabilitytests/' + id + '/')
        .error(function() {
          toastService.add('error', gettext('Error deleting reachability test'));
        });
    }

    /**
     * //////////////////////////////////////////
     * QUICK TESTS
     * //////////////////////////////////////////
     */

    /**
     * @name reachabilityquicktest_get
     * @param {Object} test - The test
     * @description Get the reachability quick test.
     *
     * @returns {Object} The result of the get call.
     */
    function reachabilityquicktest_get() {
      return apiService.get('api/neutron/reachabilityquicktest/')
        .error(function () {
          toastService.add('error', gettext('Error getting reachability quick test'));
        });
    }

    /**
     * @name reachabilityquicktest_create
     * @param {Object} test - The test
     * @description Create a reachability quick test.
     *
     * @returns {Object} The result of the creation call.
     */
    function reachabilityquicktest_create(test) {
      return apiService.post('api/neutron/reachabilityquicktest/', test)
        .error(function () {
          toastService.add('error', gettext('Error creating reachability test'));
        });
    }

    /**
     * @name reachabilityquicktest_patch
     * @param {Object} test - The test
     * @description Patch a reachability quick test.
     * Call with run_test=True to run the test.
     *
     * @returns {Object} The result of the patch call.
     */
    function reachabilityquicktest_update(test) {
      return apiService.patch('api/neutron/reachabilityquicktest/', test)
        .error(function () {
          toastService.add('error', gettext('Error patching reachability test'));
        });
    }

    /**
     * //////////////////////////////////////////
     * ADMIN NETWORK TEMPLATES
     * //////////////////////////////////////////
     */

    /**
     * @name networktemplate_create
     * @description Create a network template.
     *
     * @returns The result of the creation call.
     */
    function networktemplate_create(template) {
      return apiService.post('api/neutron/networktemplate/', template)
        .error(function() {
          toastService.add('error', gettext('Error creating network template'));
        });
    }

    /**
     * @name networktemplate_list
     * @description Get the list of network templates.
     *
     * @returns {Object} An object with property "items." Each item is a template.
     */
    function networktemplate_list() {
      return apiService.get('api/neutron/networktemplate/')
        .error(function() {
          toastService.add('error', gettext('Error getting network templates'));
        });
    }

    /**
     * @name networktemplate_get
     * @description Get a ceratin network template.
     *
     * @returns The network template.
     */
    function networktemplate_get(id) {
      return apiService.get('api/neutron/networktemplate/' + id + '/')
        .error(function() {
          toastService.add('error', gettext('Error getting network template'));
        });
    }

    /**
     * @name networktemplate_update
     * @description Update a network template
     *
     * @returns The result of the patch call.
     */
    function networktemplate_update(id, template) {
      return apiService.patch('api/neutron/networktemplate/' + id + '/', template)
        .error(function() {
          toastService.add('error', gettext('Error updating network template'));
        });
    }

    /**
     * @name networktemplate_delete
     * @description Delete a network template.
     *
     * @returns The result of the deletion call.
     */
    function networktemplate_delete(id) {
      return apiService.delete('api/neutron/networktemplate/' + id + '/')
        .error(function() {
          toastService.add('error', gettext('Error deleting network template'));
        });
    }

    /**
     * //////////////////////////////////////////
     * NETWORK TEMPLATE ASSIGNMENT
     * //////////////////////////////////////////
     */

    /**
     * @name heatstack_delete
     * @description Delete the heat stack.
     *
     * @returns The result of the deletion call.
     */
    function heatstack_delete(id) {
      return apiService.delete('api/heat/stack/' + id + '/')
        .error(function() {
          toastService.add('error', gettext('Error deleting heat stack'));
        });
    }

    /**
     * @name heatstack_create
     * @description Create a heat stack.
     *
     * @returns The result of the creation call.
     */
    function heatstack_create(stack) {
      return apiService.post('api/heat/stack/', stack)
        .error(function() {
          toastService.add('error', gettext('Error creating heat stack'));
        });
    }

    /**
     * @name check_status
     * @description Check on the status of a heat stack.
     *
     * @returns The heat stack, which has field status.
     */
    function check_status(id){
      return apiService.get('api/heat/stack/' + id + '/')
        .error(function() {
          toastService.add('error', gettext('Error checking heat stack status'));
        });
    }

    /**
     * @name template_validate
     * @description Get a list of fields needed for applying the network template
     * parsed from the body.
     *
     * @returns The result of the validate call.
     */
    function template_validate(template) {
      return apiService.post('api/heat/templatevalidate/', template)
        .error(function() {
          toastService.add('error', gettext('Error validating template'));
        });
    }

    /**
     * @name networktemplateassignment_create
     * @description Create a network template assignment.
     *
     * @returns The result of the creation call.
     */
    function networktemplateassignment_create(assignment) {
      return apiService.post('api/neutron/networktemplateassignment/', assignment)
        .error(function() {
          toastService.add('error', gettext('Error applying network template assignment'));
        });
    }

    /**
     * @name networktemplateassignment_list
     * @description Get a list of network template assignments.
     * There should only be one, and the list should contain that one
     * assignment.
     *
     * @returns The result of the list call.
     */
    function networktemplateassignment_list() {
      return apiService.get('api/neutron/networktemplateassignment/')
        .error(function() {
          toastService.add('error', gettext('Error getting network template assignment'));
        });
    }

    /**
     * @name networktemplateassignment_update
     * @description Update a network template assignment.
     * For use after a heat stack creation has begun, and a
     * stack id is available.
     *
     * @returns The result of the update call.
     */
    function networktemplateassignment_update(assignment) {
      return apiService.patch('api/neutron/networktemplateassignment/', assignment)
        .error(function() {
          toastService.add('error', gettext('Error patching network template assignment'));
        });
    }

    /**
     * @name networktemplateassignment_delete
     * @description Delete a network template assignment.
     *
     * @returns The result of the deletion call.
     */
    function networktemplateassignment_delete(id) {
      return apiService.delete('api/neutron/networktemplateassignment/' + id + '/').then(
        function success(response) {
          return response;
        },
        function error() {
          toastService.add('error', gettext('Error deleting network template assignment'));
        }
      );
    }

    /**
     * //////////////////////////////////////////
     * ROUTER RULES
     * //////////////////////////////////////////
     */

    /**
     * @name router_get
     * @description Get the router associated w/ current tenant.
     *
     * @returns The result of the get call.
     */
    function router_get() {
      return apiService.get('api/neutron/router/')
        .error(function() {
          toastService.add('error', gettext('Error getting router id'));
        });
    }

    /**
     * @name router_update
     * @description Update a router. We use this 
     *
     * @returns The result of the deletion call.
     */
    function router_update(router) {
      return apiService.patch('api/neutron/router/', router)
        .error(function() {
          toastService.add('error', gettext('Error updating router'));
        });
    }

  }

}());
