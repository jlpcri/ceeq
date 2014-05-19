
$(document).ready(function() {
    $('#subnav-tabs').find('a[href="#projects"]').tab('show');

    $.getJSON("{% url 'fetch_projects_score' %}").done(function(data){

        $('#score_container').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Quality of Solution Score Overall'
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
                    text: 'Score'
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
            credits: false
        })
    });

    $('#update_all').click(function () {
        showThrobber();
    });
    $('#update_single').click(function () {
        showThrobber();
    });
});

function showThrobber() {
    $('#throbber').show();
}



