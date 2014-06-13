$(document).ready(function() {

    Highcharts.setOptions({
                        colors: ['#CC6600', '#FF0000', '#CCCC00', '#404040', '#990099', '#000033','#663300']
    });
    $.getJSON("{% url 'fetch_projects_score' %}").done(function(data){
        console.log(data);
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
                        y:-1
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

