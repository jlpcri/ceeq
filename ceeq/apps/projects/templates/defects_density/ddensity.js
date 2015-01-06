$(document).ready(function() {
    $('#subnav-tabs').find('a[href="#dd_detail"]').tab('show');

    Highcharts.setOptions({
                colors: ['#CC6600', '#00CCCC', '#CCCC00', '#000066', '#990099', '#006600']
            });
    //var versions = [];
    $.getJSON("{% url 'fetch_defects_density_score' project.id %}").done(function(data) {
        for (var key in data){
            //versions.push(key);
            $("#dd_trend_graph_"+key).highcharts({
                title: {
                    text: 'Defect Impact Trending Graph',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Affected Version:'+key,
                    x: -20
                },
                xAxis: {
                    title: {
                        text: 'Timeline'
                    },
                    categories: data[key]['categories'],
                    labels: {
                        //rotation: -45,
                        style: {
                            fontSize: '10px'
                        }
                    },
                    tickInterval: 10
                },
                yAxis: {
                    title: {
                        text: 'Defects Density score'
                    },
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                tooltip: {
                    valueSuffix: ''
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAligh: 'middle',
                    borderWidth: 0
                },
                navigation: {
                    buttonOptions: {
                        enabled: false
                    }
                },
                series: [{
                    name: 'CXP',
                    data: data[key]['cxp']
                },{
                    name: 'Platform',
                    data: data[key]['platform']
                },{
                    name: 'Reports',
                    data: data[key]['reports']
                },{
                    name: 'Application',
                    data: data[key]['application']
                },{
                    name: 'VoicePrompts',
                    data: data[key]['voiceSlots']
                }],
                credits: false
            });

            $("#ceeq_trend_graph_"+key).highcharts({
                title: {
                    text: 'CEEQ Score Average: <b>' + data[key]['ceeq_average'] + ' / 10</b>',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Affected Version:'+key,
                    x: -20
                },
                xAxis: {
                    title: {
                        text: 'Timeline'
                    },
                    categories: data[key]['categories'],
                    labels: {
                        //rotation: -45,
                        style: {
                            fontSize: '10px'
                        }
                    },
                    tickInterval: 10
                },
                yAxis: {
                    title: {
                        text: 'CEEQ Score'
                    },
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                tooltip: {
                    valueSuffix: ''
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAligh: 'middle',
                    borderWidth: 0
                },
                navigation: {
                    buttonOptions: {
                        enabled: false
                    }
                },
                series: [{
                    name: 'CEEQ',
                    data: data[key]['ceeq']
                }],
                credits: false
            });
        }
    });

    $.getJSON("{% url 'fetch_dds_json' project.id %}").done(function(data) {
        $('#dd_list_single').html('<table cellpadding="0" cellspacing="0" border="0" class="display" id="dd_list_single_table"></table>');
        $('#dd_list_single_table').dataTable({
            "data":data,
            "columns": [
                {"title": "Project"},
                {"title": "Version"},
                {"title": "Date"},
                {"title": "CXP"},
                {"title": "Platform"},
                {"title": "Reports"},
                {"title": "Application"},
                {"title": "Voice Slots"},
                {"title": "CEEQ"}
            ],
            "language": {
                "decimal": ",",
                "thousands": "."
            }
        });
    });
});


var today = new Date();
var export_filename = '{{ project.name }}' + '-' + today.toLocaleDateString();
function exportGraphCeeq(type, version){
    //console.log(version);
    var chart = $('#ceeq_trend_graph_'+version).highcharts();
    chart.exportChart({
        type: type,
        scale: 1, //800 * 400
        filename: 'Trending-CEEQ-' + export_filename
    });
}

function exportGraphDefectImpact(type, version){
    //console.log(version);
    var chart = $('#dd_trend_graph_'+version).highcharts();
    chart.exportChart({
        type: type,
        scale: 1, //800 * 400
        filename: 'Trending-DI-' + export_filename
    });
}