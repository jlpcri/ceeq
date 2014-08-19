$(document).ready(function() {

    Highcharts.setOptions({
        //colors: ['#CC6600', '#00CCCC', '#CCCC00', '#000066', '#990099', '#006600']
    });
    $.getJSON("{% url 'fetch_projects_score' %}").done(function(data){
        //console.log(data);
        $('#home_score_container').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Comprehensive End to End Quality Overall'
            },
            xAxis: {
                title: {
                    text: 'Projects'
                },
                categories: data['categories']
            },
            yAxis: {
                min: 0,
                max: 10,
                title: {
                    text: 'CEEQ Score'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                bar: {
                    colorByPoint: true,
                    dataLabels: {
                        enabled:true,
                        align:"right",
                        color:"#FFFFFF",
                        x:-10,
                        y:-1,
                        formatter: function(){
                            return this.y.toFixed(2)
                        }
                    }
                },
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function(){
                                location.href = '/ceeq/project/' + data['id'][this.x];
                            }
                        }
                    }
                }
            },
            series: [{
                data: data['score'].map(Number)
            }],
            tooltip: {
                formatter: function() {
                    return this.x + ': ' + this.y
                }
            },
            navigation: {
                buttonOptions: {
                    enabled: false
                }
            },
            credits: false
        })
    });

});

