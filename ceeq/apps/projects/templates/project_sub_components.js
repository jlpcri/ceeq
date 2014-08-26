//button handler
var today = new Date();
var export_filename = 'app_sub' + '-' +today.toLocaleDateString();
$('#pdf').click(function () {
    var chart = $('#apps_subcomponent_percentage_pie_chart').highcharts();
    chart.exportChart({
        type: 'application/pdf',
        scale: 1,
        width: 550,
        filename: export_filename
    });
});
$('#jpeg').click(function () {
    var chart = $('#apps_subcomponent_percentage_pie_chart').highcharts();
    chart.exportChart({
        type: 'image/jpeg',
        scale: 1,
        filename: export_filename
    });
});
$('#png').click(function () {
    var chart = $('#apps_subcomponent_percentage_pie_chart').highcharts();
    chart.exportChart({
        type: 'image/png',
        scale: 1,
        //sourceWidth: 1000,
        //sourceHeight: 300,
        filename: export_filename
    });
});

function draw_pie_chart_graph(data){
    //Create the data table
    Highcharts.drawTable = function() {

        // user options
        var row_label = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial', 'Subtotal'];
        var row_orc_label = ['O', 'R', 'C',
                            'O', 'R', 'C',
                            'O', 'R', 'C',
                            'O', 'R', 'C',
                            'O', 'R', 'C'
                            ];
        var tableTop = 350,
            colWidth = 30,
            tableLeft = 80,
            rowHeight = 25,
            cellPadding = 2.5,
            valueDecimals = 3;

        // internal variables
        var chart = this,
            renderer = chart.renderer,
            cellLeft = tableLeft;

        // draw components lables
        $.each(data[1], function(i, item) {
            //console.log(item);
            renderer.text(
                item[0],
                cellLeft + cellPadding,
                tableTop + (i + 3) * rowHeight - cellPadding
            )
            .css({
                fontWeight: 'bold',
                fontSize: '10pt'
            })
            .add();
        });

        // draw jira priority lables
        cellLeft += colWidth;
        $.each(row_label, function(i, item) {
            cellLeft += colWidth * 3;

            renderer.text(
                item,
                cellLeft - cellPadding + colWidth,
                tableTop + rowHeight - cellPadding
            )
            .attr({
                align: 'center'
            })
            .css({
                fontWeight: 'bold',
                fontSize: '10pt'
            })
            .add();
            //draw vertical line
            Highcharts.tableLine(
                renderer,
                cellLeft - cellPadding * 6,
                tableTop + rowHeight + cellPadding,
                cellLeft - cellPadding * 6,
                tableTop + (data[1].length + 3) * rowHeight + cellPadding
            );
        });

        // draw jira priority Open Resolved Closed lables
        cellLeft = tableLeft + colWidth * 2;
        $.each(row_orc_label, function(i, item) {
            cellLeft += colWidth;

            renderer.text(
                item,
                cellLeft - cellPadding + colWidth,
                tableTop + rowHeight * 2 - cellPadding
            )
            .attr({
                align: 'center'
            })
            .css({
                fontStyle: 'italic',
                fontSize: '10pt',
                color: 'blue'
            })
            .add();
        });

        $.each(data[1], function(row, item){
            cellLeft = tableLeft + colWidth * 2;

            // apply number of jiras
            $.each(item, function(i, priority){
                cellLeft += colWidth;
                if (i > 0){
                    renderer.text(
                        priority,
                        cellLeft - cellPadding,
                        tableTop + (row + 3) * rowHeight -cellPadding
                    )
                    .attr({
                        align: 'center'
                    })
                    .css({
                        fontSize: '10pt'
                    })
                    .add();
                }
            });

            if (row == 0){
                Highcharts.tableLine( // top
                    renderer,
                    tableLeft,
                    tableTop + cellPadding,
                    cellLeft + colWidth * 1.5,
                    tableTop + cellPadding
                );

                // last three rows
                for (var i = 1; i < 4; i++) {
                    Highcharts.tableLine( // bottom - 1
                    renderer,
                    tableLeft,
                    tableTop + (data[1].length + i) * rowHeight + cellPadding,
                    cellLeft + colWidth * 1.5,
                    tableTop + (data[1].length + i) * rowHeight + cellPadding
                    );
                }

            }
            // horizontal line
            Highcharts.tableLine(
                renderer,
                tableLeft,
                tableTop + row * rowHeight + rowHeight + cellPadding,
                cellLeft + colWidth * 1.5,
                tableTop + row * rowHeight + rowHeight + cellPadding
            );
        });

        cellLeft = tableLeft + colWidth * 2;
        $.each(data[2], function(i, priority_total) {
            cellLeft  += colWidth;
            if ( i > 0) {
                renderer.text(
                    priority_total,
                    cellLeft - cellPadding,
                    tableTop + (data[1].length + 3) * rowHeight - cellPadding
                )
                .attr({
                    align: 'center'
                })
                .css({
                    fontWeight: 'bold',
                    fontSize: '10pt'
                })
                .add();
            }
            else {
                renderer.text(
                    priority_total,
                    tableLeft + cellPadding,
                    tableTop + (data[1].length + 3) * rowHeight - cellPadding
                )
                .css({
                    fontWeight: 'bold',
                    fontSize: '10pt'
                })
                .add();
            }

        });

    };

    //Draw a single line in the table
    Highcharts.tableLine = function (renderer, x1, y1, x2, y2) {
        renderer.path(['M', x1, y1, 'L', x2, y2])
            .attr({
                'stroke': 'black',
                'stroke-width': 1
            })
            .add();
    };

    Highcharts.setOptions({
        //colors: ['#CC6600', '#00CCCC', '#CCCC00', '#000066', '#990099', '#006600']
    });
    var pie_title = title + ' Subcomponent';

    $('#apps_subcomponent_percentage_pie_chart').highcharts({
        chart: {
            //plotBackgroundColor: null,
            //plotBorderWidth: null,
            //plotShadow: false,
            events: {
                load: Highcharts.drawTable
            },
            style: {
                fontFamily: 'serif'
            },
            borderWidth: 0
        },
        title: {
            text: pie_title,
            style: {
                fontSize: '18pt',
                color: '#000000'
            },
            align: 'left'
        },
        tooltip: {
            //pointFormat: '{series.name}: <b>{point.percentage:.2f}%</b>'
            formatter: function() {
                return this.point.name + ": <b>" + this.point.percentage.toFixed(2) + "%</b>";
            }
        },
        plotOptions: {
            pie: {
                //allowPointSelect: true,
                cursor: 'pointer',
                center: ['50%', 100],
                size: '40%',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.2f}%',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    },
                    overflow: 'none'
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Component Contribution',
            data: data[0]
        }],
        navigation: {
            buttonOptions: {
                enabled: false
            }
        },
        credits: false
    });
}

