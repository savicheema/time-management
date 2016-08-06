(function() {
  'use strict';
  angular.module('MyApp',['ngMaterial', 'ngMessages'])
      .controller('AppCtrl', AppCtrl);

  function AppCtrl($scope) {
    $scope.currentNavItem = 'page1';
    $scope.summary = summary;
  }
})();