$(document).ready(function() {

//    Highcharts.setOptions({
//        //colors: ['#CC6600', '#00CCCC', '#CCCC00', '#000066', '#990099', '#006600']
//        colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
//            '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1',
//            '#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce',
//            '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'
//        ]
//    });

    /**
     * Sand-Signika theme for Highcharts JS
     * @author Torstein Honsi
     */

    // Load the fonts
    Highcharts.createElement('link', {
       href: '//fonts.googleapis.com/css?family=Signika:400,700',
       rel: 'stylesheet',
       type: 'text/css'
    }, null, document.getElementsByTagName('head')[0]);

    // Add the background image to the container
    Highcharts.wrap(Highcharts.Chart.prototype, 'getContainer', function (proceed) {
       proceed.call(this);
       this.container.style.background = 'url(http://www.highcharts.com/samples/graphics/sand.png)';
    });


    Highcharts.theme = {
//       colors: ["#f45b5b", "#8085e9", "#8d4654", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee",
//          "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
       colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
           '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1',
           '#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce',
           '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'
       ],
       chart: {
          backgroundColor: null,
          style: {
             fontFamily: "Signika, serif"
          }
       },
       title: {
          style: {
             color: 'black',
             fontSize: '20px',
             fontWeight: 'bold'
          }
       },
       subtitle: {
          style: {
             color: 'black'
          }
       },
       tooltip: {
          borderWidth: 0
       },
       legend: {
          itemStyle: {
             fontWeight: 'bold',
             fontSize: '13px'
          }
       },
       xAxis: {
          labels: {
             style: {
                 color: '#6e6e70',
                 fontWeight: 'bold'
             }
          }
       },
       yAxis: {
          labels: {
             style: {
                color: '#6e6e70'
             }
          }
       },
       plotOptions: {
          series: {
             shadow: true
          },
          candlestick: {
             lineColor: '#404048'
          },
          map: {
             shadow: false
          }
       },

       // Highstock specific
       navigator: {
          xAxis: {
             gridLineColor: '#D0D0D8'
          }
       },
       rangeSelector: {
          buttonTheme: {
             fill: 'white',
             stroke: '#C0C0C8',
             'stroke-width': 1,
             states: {
                select: {
                   fill: '#D0D0D8'
                }
             }
          }
       },
       scrollbar: {
          trackBorderColor: '#C0C0C8'
       },

       // General
       background2: '#E0E0E8'

    };


    Highcharts.setOptions(Highcharts.theme);

    $.getJSON("{% url 'queries:fetch_projects_score' %}").done(function(data){
        //console.log(data);
        var i, min_yaxis, min = data['score'][0];
        for (i = 1; i < data['score'].length; i++) {
            if (data['score'][i] < min) {
                min = data['score'][i];
            }
        }
        if (min < 0) {
            min_yaxis = Math.floor(min);
        } else {
            min_yaxis = 0;
        }

        $('#home_score_container').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Comprehensive End to End Quality Overall'
            },
            xAxis: {
//                title: {
//                    text: 'Projects',
//                    style: {
//                        fontSize: '18px'
//                    }
//                },
                categories: data['categories']
            },
            yAxis: {
                min: min_yaxis,
                max: 10,
                tickInterval: 0.5,
                title: {
                    text: 'CEEQ Score',
                    style: {
                        fontSize: '18px'
                    }
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
                        x: 0,
                        y: -1,
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
                                location.href = '{{root_path}}' + 'queries/' + data['id'][this.x];
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

    $.getJSON("{% url 'queries:fetch_projects_score' %}").done(function(data){
        //console.log(data);
        var rawData = [],
            ticks = [],
            project_ids = [];

        project_ids = data['id'].reverse();
        var colors =  ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
           '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1',
           '#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce',
           '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'
        ];

        $.each(data['categories'].reverse(), function(k, v){
            ticks.push([k, v]);
        });
        $.each(data['score'].reverse(), function(k, v){
            rawData.push({
                data: [[parseFloat(v), k]],
                color: colors[k]
            });
        });

        var dataSet = [{ label: "", data: rawData, color: '' }];

        var options = {
            series: {
                bars: {
                    show: true
                }
            },
            bars: {
                align: "center",
                barWidth: 0.5,
                horizontal: true,
                fillColor: { colors: [{ opacity: 0.5 }, { opacity: 1}] },
                lineWidth: 1
            },
            xaxis: {
                axisLabel: "CEEQ Score",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 1,
                max: 10,
                tickColor: "#5E5E5E",
                tickFormatter: function (v, axis) {
                    return v;
                },
                color: "black"
            },
            yaxis: {
                axisLabel: "Project",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 3,
                tickColor: "#5E5E5E",
                ticks: ticks,
                color: "black"
            },
            legend: {
                noColumns: 0,
                labelBoxBorderColor: "#858585",
                position: "ne"
            },
            grid: {
                hoverable: true,
                borderWidth: 2,
                backgroundColor: { colors: [] },
                clickable: true
            }
        };

        $.plot($('#home_score_flot'), rawData, options);
        $('#home_score_flot').UseTooltip();
        $('#home_score_flot').bind('plotclick', function(event, pos, item) {
            if (item) {
                var x = item.datapoint[0];
                var y = item.datapoint[1];
                location.href = '{{root_path}}' + 'queries/' + project_ids[y];
            }
        })

    })

});

var previousPoint = null, previousLabel = null;

$.fn.UseTooltip = function () {
    $(this).bind("plothover", function (event, pos, item) {
        if (item) {
            if ((previousLabel != item.series.label) ||
            (previousPoint != item.dataIndex)) {
                previousPoint = item.dataIndex;
                previousLabel = item.series.label;
                $("#tooltip").remove();

                var x = item.datapoint[0];
                var y = item.datapoint[1];

                var color = item.series.color;
                //alert(color)
                //console.log(item.series.xaxis.ticks[x].label);

                showTooltip(item.pageX,
                item.pageY,
                color,
                item.series.yaxis.ticks[y].label +
                " : <strong>" + x + "</strong>");
            }
        } else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
};

function showTooltip(x, y, color, contents) {
    $('<div id="tooltip">' + contents + '</div>').css({
        position: 'absolute',
        display: 'none',
        top: y - 10,
        left: x + 10,
        border: '2px solid ' + color,
        padding: '3px',
        'font-size': '9px',
        'border-radius': '5px',
        'background-color': '#fff',
        'font-family': 'Verdana, Arial, Helvetica, Tahoma, sans-serif',
        opacity: 0.9
    }).appendTo("body").fadeIn(200);
}
