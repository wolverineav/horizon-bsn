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
    .module('horizon.framework.widgets.table')
    .directive('extendedHzResourceTable', directive);

  directive.$inject = ['bsn.bsndashboard.networktemplateassignment.basePath'];

  /**
   * @ngdoc directive
   * @name extendedHzResourceTable
   * Note: This directive is the same as the hz-resource-table from upstream
   * Horizon, but has some extra functionalities for the requirements of the
   * network template assignment panel.
   * @description
   * This directive produces a table and accompanying components that describe
   * a list of resources of the given type.  Based on information in the
   * registry, the batch, global, and item-level actions are presented as
   * appropriate.  Search capabilities are also provided.  The table contents
   * are responsive to actions' promise resolutions, updating contents when
   * they are likely to have changed.  This directive allows for the rapid
   * development of standard resource tables without having to rewrite
   * boilerplate controllers, markup, etc.
   * @example
   ```
   <div>Here's some content above the table.</div>
   <hz-resource-table resource-type-name="OS::Cinder::Volume"></hz-resource-table>
   <div>Here's some content below the table.</div>
   ```
   */

  function directive(basePath) {

    var directive = {
      restrict: 'E',
      scope: {
        resourceTypeName: '@',
        trackBy: '@?'
      },
      bindToController: true,
      templateUrl: basePath + 'table/extended-hz-resource-table.html',
      controller: "horizon.framework.widgets.table.ExtendedResourceTableController as ctrl"
    };

    return directive;
  }
})();
