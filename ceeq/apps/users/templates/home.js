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

    $.getJSON("{% url 'q_fetch_projects_score' %}").done(function(data){
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
                                location.href = '/ceeq/queries/' + data['id'][this.x];
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

