
$(document).ready(function(){
    $.getJSON("{% url 'get_project_access_trend' %}").done(function(data){
        var chart_export = new Highcharts.Chart({
            chart: {
                renderTo: 'usage_project_access'
            },
            title: {
                text: 'Project Visited Trend Graph',
                style: {
                    font: '18pt "Lucida Grande", Helvetica, Arial, sans-serif'
                }
            },
            xAxis: {
                title: {
                    text: 'Timeline'
                },
                categories: data['categories'],
                labels: {
                    formatter: function(){
                        return this.value.substring(5);
                    },
                    style: {
                        fontSize: '10px'
                    }
                },
                tickInterval: Math.floor(data['categories'].length / 10)
            },
            yAxis: {
                title: {
                    text: 'Total # visited per day'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function () {
                    var s = '<b>' + this.x + '</b>';
                    $.each(this.points, function(){
                        var names = '';
                        $.each(this.point.extra, function(index, value){
                            names += value + '<br>';
                        });
                        s += '<br>' + this.series.name + ': <b>' + this.y + '</b>' + '<br>' + names;
                    });
                    return s;
                },
                valueSuffix: '',
                shared: true
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            navigation: {
                buttonOptions: {
                    enabled: false
                }
            },
            plotOptions: {
                series: {
                    maker: {
                        enabled: false
                    }
                }
            },
            series: [
                {
                    name: 'Total Access',
                    data: data['count']
                }
            ],
            credits: false
        })
    })
});
