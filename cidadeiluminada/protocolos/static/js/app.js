'use strict';

var services = angular.module('protocolosServices', []);
/* Services */

services.factory('protocolosAPI', ['$http', '$filter',
    function($http, $filter){
        var protocolosAPI = {};

        protocolosAPI.getProtocolos = function getProtocolos(cod_protocolo) {
            var data = {};
            if (cod_protocolo) {
                data['cod_protocolo'] = cod_protocolo
            }
            return _get('protocolos.json', data);
        };

        protocolosAPI.sendStatus = function sendStatus(protocolo_id, status) {
            var data = {
                protocolo_id: protocolo_id,
                status: status,
            };
            return _post('/status/', data);
        }

        var _get = function(url, params) {
            return $http({
                method: 'GET',
                url: '/protocolos/' + url,
                params: params
            });
        }

        var _post = function (url, data) {
            return $http({
                method: 'POST',
                url: '/protocolos/' + data['protocolo_id'] + url,
                data: data
            });
        }

        return protocolosAPI;
    }
]);


var protocolosControllers = angular.module('protocolosControllers', ['pusher-angular']);

var pusherClient = new Pusher(window.pusherToken, {
    encrypted: true
})

protocolosControllers.controller('ProtocolosListaController', ['$scope', '$filter', '$pusher', 'protocolosAPI',
  function($scope, $filter, $pusher, protocolosAPI) {
    moment.locale('pt-br');

    $scope.statusProtocolos = ['NOVO', 'INVALIDO', 'PROCESSADO'];
    $scope.statusProtocolosOptions = {
        'NOVO': 'Novos',
        'INVALIDO': 'Inválidos',
        'PROCESSADO': 'Processados',
    };

    $scope.filters = {
        'status': null,
        'pesquisa': null,
    }

    $scope.initProtocolo = function initProtocolo(protocolo) {
        protocolo._status = protocolo.status;
    }

    $scope.loadProtocolos = function loadProtocolos(cod_protocolo) {
        return protocolosAPI
                .getProtocolos(cod_protocolo)
                .then(function(response) {
                    var protocolos = response.data.protocolos;
                    angular.forEach(protocolos, function(protocolo, i){
                        $scope.initProtocolo(protocolo);
                    });
                    $scope.protocolos = protocolos;
                });
    };

    $scope.sendStatus = function sendStatus(protocolo, status) {
        return protocolosAPI
            .sendStatus(protocolo.id, status)
            .then(function(response) {
                console.log(response.data);
            });
    };

    $scope.filterProtocolos = function filterProtocolos(filter) {
        return function(protocolo) {
            if (filter === null) {
                return true;
            }
            return filter == protocolo.status;
        }
    }

    $scope.reloadProtocolos = function reloadProtocolos(filters) {
        $scope.loadProtocolos(filters.pesquisa);
    }

    $scope.cleanPesquisa = function cleanPesquisa() {
        $scope.filters.pesquisa = null;
        $scope.reloadProtocolos($scope.filters);
    }

    var pusher = $pusher(pusherClient),
        protocolos_channel = pusher.subscribe("cidadeiluminada");

    protocolos_channel.bind('novo-protocolo', function(protocolo) {
        $scope.initProtocolo(protocolo);
        $scope.protocolos.unshift(protocolo);
        $scope.notification('Novo protocolo', protocolo.cod_protocolo);
    });

    protocolos_channel.bind('atualiza-protocolo', function(data) {
        var id = data['protocolo_id'];
        angular.forEach($scope.protocolos, function(protocolo, i) {
            if (protocolo.id == id) {
                for (var key in data) {
                    protocolo[key] = data[key];
                }
            }
        });
    });

    $scope.notification = function(title, body) {
        if (Notification.permission === "granted") {
            new Notification(title, {body: body})
        }
    }

    $scope.loadProtocolos();
    Notification.requestPermission();
  }
]);

var protocolosDirectives = angular.module('protocolosDirectives', []);
/* Directives */

protocolosDirectives.directive('elapsedTimeSince', function($interval, dateFilter) {
    moment.lang('pt-br')
    var link = function(scope, element, attrs) {
        function pad(num) {
            var s = "0" + num;
            return s.substr(s.length-2);
        }

        var timeoutId,
            initialTime = moment(scope.time);

        function updateTime() {
            var diffms = moment().diff(initialTime),
                duration = moment.duration(diffms);
            if (duration.days() > 0){
                element.text(duration.humanize())
            } else {
                element.text(pad(duration.hours()) + ':' + pad(duration.minutes()) + ':' + pad(duration.seconds()));
            }
        }

        scope.$watch(attrs.elapsedTimeSince, function(value) {
            updateTime();
        });

        timeoutId = $interval(updateTime, 1000);

        element.on('$destroy', function() {
            $interval.cancel(timeoutId);
        });
    }
    return {
        restrict: 'A',
        scope : {
            time: '='
        },
        link: link
    };
});

protocolosDirectives.directive('ngEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keydown", function (event) {
            if(event.which === 13) {
                scope.$apply(function (){
                    scope.$eval(attrs.ngEnter);
                });
                event.preventDefault();
            }
        });
    };
});

var protocolosFilters = angular.module('protocolosFilters', []);
/* Filters */

protocolosFilters.filter('checkmark', function() {
    return function(input) {
        return input ? '\u2713' : '\u2718';
    };
});

var protocolosApp = angular.module('protocolosApp', [
    'protocolosFilters',
    'protocolosServices',
    'protocolosControllers',
    'protocolosDirectives',
]);

protocolosApp.constant('moment', moment)

protocolosApp.config(['$interpolateProvider',
    function($interpolateProvider) {
        $interpolateProvider.startSymbol('[[').endSymbol(']]');
     }
 ]);



