$(document).ready(function() {
            $('#subnav-tabs').find('a[href="#dd_detail"]').tab('show');
            $.getJSON("{% url 'fetch_defects_density_score' project.id %}").done(function(data) {
                for (var key in data){
                    $("#dd_trend_graph_"+key).highcharts({
                        title: {
                            text: 'Defects Density Trending Graph',
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
                            categories: data[key]['categories']
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
                        series: [{
                            name: 'CXP',
                            data: data[key]['cxp']
                        },{
                            name: 'Outbound',
                            data: data[key]['outbound']
                        },{
                            name: 'Platform',
                            data: data[key]['platform']
                        },{
                            name: 'Reports',
                            data: data[key]['reports']
                        },{
                            name: 'Applications',
                            data: data[key]['applications']
                        },{
                            name: 'VoiceSlots',
                            data: data[key]['voiceSlots']
                        }]
                    });
                }
            })
        });
