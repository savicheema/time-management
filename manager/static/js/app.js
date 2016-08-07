(function() {
  'use strict';
  angular.module('MyApp',['ngMaterial', 'ngMessages'])
      .controller('AppCtrl', AppCtrl);

  function AppCtrl($scope) {
    $scope.currentNavItem = 'page1';
    $scope.summary = summary;

    $scope.GoToProject = function(url, projectID){
    window.location.href = url.replace('projectid', projectID);
    }
  }
})();