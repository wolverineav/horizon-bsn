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

  /**
   * @ngdoc ApplyNetTemplateController
   * @ngController
   *
   * @description
   * Controller for applying a network template.
   */

  angular
    .module('bsn.bsndashboard.networktemplateassignment.actions')
    .controller('SelectNetTemplateController', selectController);

    selectController.$inject = [
      'horizon.app.core.openstack-service-api.bsnneutron',
      '$scope'
    ]

  /**
   * This controller controls both modals that show when applying a network template.
   */
  function selectController(bsnneutron, $scope) {
    var ctrl = this;
    ctrl.model = {};
    ctrl.templates = [];

    if ($scope.properties) {
      var parameters = $scope.properties.Parameters;
      for (var parameter in parameters) {
         ctrl.model[parameter] = parameters[parameter].Default;
      }
      ctrl.params = $scope.properties.Parameters;
    }
    
    bsnneutron.networktemplate_list().then(function (result){
      ctrl.templates = result.data.items;
    });


  }
})();
