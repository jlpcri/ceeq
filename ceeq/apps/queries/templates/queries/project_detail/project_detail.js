var active_tab = String(""),
    donut_pie,
    today = new Date(),
    export_filename = '{{ project.name}}' + '-' + today.toISOString().slice(0, 10);
    //export_trend_filename = '{{ project.name}}' + '-trend-' + today.toLocaleDateString();

moment.tz.add('America/Chicago|CST CDT|60 50|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');
var startDatetime = moment.tz(moment().valueOf(), 'America/Chicago');
var endDatetime = moment.tz(moment().valueOf(), 'America/Chicago');
var uat_type_custom = $('#custom-uat-type > select').val();

function setStartDate(datetime) {
    startDatetime = moment.tz(moment(datetime*1000), 'America/Chicago');
//    startDatetime = moment(datetime*1000);
}

function setEndDate(datetime) {
    endDatetime = moment.tz(moment(datetime*1000), 'America/Chicago');
//    endDatetime = moment(datetime*1000);
}

function loadRecords() {
    $('#custom_pie_chart_loading').show();
    $('#custom_pie_chart_contents').hide();
    window.location.href = "{% url 'queries:project_detail' project.id %}?start=" + startDatetime.format('X') + "&end=" + endDatetime.format('X') + "&uat_type_custom=" + uat_type_custom + "&last_tab=custom";
}

function attachDateRangePicker() {
    $('#report-range').daterangepicker(
        {
            ranges: {
                'Today': [moment.tz(moment().valueOf(), 'America/Chicago').startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('day')],
                'Yesterday': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 1).startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 1).endOf('day')],
                'Last 7 Days': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 6).startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('day')],
                'Last 30 Days': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('days', 29).startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('day')],
                'This Month': [moment.tz(moment().valueOf(), 'America/Chicago').startOf('month').startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').endOf('month').endOf('day')],
                'Last Month': [moment.tz(moment().valueOf(), 'America/Chicago').subtract('month', 1).startOf('month').startOf('day'), moment.tz(moment().valueOf(), 'America/Chicago').subtract('month', 1).endOf('month').endOf('day')]
            },
            startDate: moment.tz(startDatetime.valueOf(), 'America/Chicago'),
            endDate: moment.tz(endDatetime.valueOf(), 'America/Chicago'),
            maxDate: moment.tz(moment().valueOf(), 'America/Chicago').endOf('day'),
            timePicker: true,
            timePickerIncrement: 1
        },
        function (start, end) {
            $('#report-range span').html(moment.tz(start.valueOf(), 'America/Chicago').format('MMMM D, YYYY HH:mm') + ' - ' + moment.tz(end.valueOf(), 'America/Chicago').endOf('day').format('MMMM D, YYYY HH:mm'));
            startDatetime = moment.tz(start.valueOf(), 'America/Chicago');
            endDatetime = moment.tz(end.valueOf(), 'America/Chicago');
            loadRecords();
        });
    $('#report-range span').html(moment.tz(startDatetime.valueOf(), 'America/Chicago').format('MMMM D, YYYY HH:mm') + ' - ' + moment.tz(endDatetime.valueOf(), 'America/Chicago').endOf('day').format('MMMM D, YYYY HH:mm'));
}

function attachUatType(){
    uat_type_custom = $('#custom-uat-type > select').val();
    loadRecords();
}

$('#subnav-tabs').find('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
    active_tab = e.target.hash;
    loadUatActiveDataTab();
});

$(document).ready(function(){
    if (last_tab == 'custom') {
        $('#subnav-tabs').find('a[href="#custom"]').tab('show');
    } else {
        $('#subnav-tabs').find('a[href="#exclude_uat"]').tab('show');
    }

    moment.tz.add('America/Chicago|CST CDT|60 50|01010101010101010101010|1BQT0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Rd0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0 Op0 1zb0');

});


function loadUatActiveDataTab() {
    var pie_chart_id = '#component_percentage_pie_chart_',
        trend_chart_id = '#ceeq_trend_chart_',
        jira_data_table_id = '#subcomponent_jira_data_table_',
        pie_chart_height = 350,
        jira_data_table_cell_height = 25,
        jira_data_table_extra_height = 150,
        div_pie_height,
        div_data_table_height,
        chart_pie_exclude_uat,
        chart_pie_include_uat,
        chart_pie_only_uat,
        chart_pie_custom,
        chart_line_exclude_uat,
        chart_line_include_uat,
        chart_data_table_exclude_uat,
        chart_data_table_include_uat,
        chart_data_table_only_uat,
        chart_data_table_custom;

    if (active_tab == '#include_uat') {
        donut_pie = 'include_uat';

        if (trend_include_uat['ceeq'].length > 0) {
            chart_line_include_uat = displayCeeqTrend(trend_include_uat, donut_pie, trend_chart_id, data_include_uat[3]);
        } else {
            $(trend_chart_id + donut_pie).hide();
            $(trend_chart_id + donut_pie + '_export').hide();
        }

        div_pie_height = pie_chart_height;
        $(pie_chart_id + donut_pie).height(div_pie_height);
        chart_pie_include_uat = displayPieChart(data_include_uat, donut_pie, pie_chart_id);

        div_data_table_height = data_include_uat[1].length * jira_data_table_cell_height + jira_data_table_extra_height;
        $(jira_data_table_id + donut_pie).height(div_data_table_height);
        chart_data_table_include_uat = displayJiraDataTable(data_include_uat, donut_pie, jira_data_table_id);

        displayQEIlogo(donut_pie);

        exportAllCharts([chart_line_include_uat, chart_pie_include_uat, chart_data_table_include_uat], donut_pie);

    } else if (active_tab == '#exclude_uat') {
        donut_pie = 'exclude_uat';

        if (trend_exclude_uat['ceeq'].length > 0) {
            chart_line_exclude_uat = displayCeeqTrend(trend_exclude_uat, donut_pie, trend_chart_id, data_exclude_uat[3]);
        } else {
            $(trend_chart_id + donut_pie).hide();
            $(trend_chart_id + donut_pie + '_export').hide();
        }

        div_pie_height = pie_chart_height;
        $(pie_chart_id + donut_pie).height(div_pie_height);
        chart_pie_exclude_uat = displayPieChart(data_exclude_uat, donut_pie, pie_chart_id);

        div_data_table_height = data_exclude_uat[1].length * jira_data_table_cell_height + jira_data_table_extra_height;
        $(jira_data_table_id + donut_pie).height(div_data_table_height);
        chart_data_table_exclude_uat = displayJiraDataTable(data_exclude_uat, donut_pie, jira_data_table_id);

        displayQEIlogo(donut_pie);

        exportAllCharts([chart_line_exclude_uat, chart_pie_exclude_uat, chart_data_table_exclude_uat], donut_pie);

    } else if (active_tab == '#only_uat') {
        donut_pie = 'only_uat';

        //div_pie_height = data_only_uat[1].length * jira_data_table_cell_height + pie_chart_height;
        //$(pie_chart_id + donut_pie).height(div_pie_height);
        //
        //chart_pie_only_uat = displayPieChart(data_only_uat, donut_pie, pie_chart_id);
        div_pie_height = pie_chart_height;
        $(pie_chart_id + donut_pie).height(div_pie_height);
        chart_pie_only_uat = displayPieChart(data_only_uat, donut_pie, pie_chart_id);

        div_data_table_height = data_only_uat[1].length * jira_data_table_cell_height + jira_data_table_extra_height;
        $(jira_data_table_id + donut_pie).height(div_data_table_height);
        chart_data_table_only_uat = displayJiraDataTable(data_only_uat, donut_pie, jira_data_table_id);

        displayQEIlogo(donut_pie);

        exportAllCharts([chart_pie_only_uat], donut_pie);
    } else if (active_tab == '#custom') {
        donut_pie = 'custom';

        //div_pie_height = data_custom[1].length * jira_data_table_cell_height + pie_chart_height;
        //$(pie_chart_id + donut_pie).height(div_pie_height);
        //
        //chart_pie_custom = displayPieChart(data_custom, donut_pie, pie_chart_id);

        div_pie_height = pie_chart_height;
        $(pie_chart_id + donut_pie).height(div_pie_height);
        chart_pie_custom = displayPieChart(data_custom, donut_pie, pie_chart_id);

        div_data_table_height = data_custom[1].length * jira_data_table_cell_height + jira_data_table_extra_height;
        $(jira_data_table_id + donut_pie).height(div_data_table_height);
        chart_data_table_custom = displayJiraDataTable(data_custom, donut_pie, jira_data_table_id);

        displayQEIlogo(donut_pie);

        exportAllCharts([chart_pie_custom], donut_pie);
    }
}

function displayPieChart(data, uat_type, pie_chart_id) {
    pie_chart_id = pie_chart_id.substring(1, pie_chart_id.length);
    var score = data[3];

    if (score < 10) {
        //Create the data table
        Highcharts.drawTable = function () {

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
                tableLeft = 25,
                rowHeight = 25,
                cellPadding = 2.5,
                valueDecimals = 3;

            // internal variables
            var chart = this,
                renderer = chart.renderer,
                cellLeft = tableLeft;

            // draw components lables
            $.each(data[1], function (i, item) {
                renderer.text(
                    item[0],
                        cellLeft + cellPadding,
                        tableTop + (i + 3) * rowHeight - cellPadding
                )
                    .css({
                        //fontWeight: 'bold',
                        //fontSize: '10pt',
                        font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'

                    })
                    .add();
            });

            // draw jira priority lables
            cellLeft += colWidth;
            $.each(row_label, function (i, item) {
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
                        //fontWeight: 'bold',
                        //fontSize: '10pt',
                        font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
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
            $.each(row_orc_label, function (i, item) {
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
                        //fontStyle: 'italic',
                        //fontSize: '10pt',
                        color: 'blue',
                        font: 'bold italic 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                    })
                    .add();
            });

            $.each(data[1], function (row, item) {
                cellLeft = tableLeft + colWidth * 2;

                // apply number of jiras
                $.each(item, function (i, priority) {
                    cellLeft += colWidth;
                    if (i > 0) {
                        renderer.text(
                            priority,
                                cellLeft - cellPadding,
                                tableTop + (row + 3) * rowHeight - cellPadding
                        )
                            .attr({
                                align: 'center'
                            })
                            .css({
                                //fontSize: '10pt'
                                font: '10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                            })
                            .add();
                    }
                });

                if (row == 0) {
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
            $.each(data[2], function (i, priority_total) {
                cellLeft += colWidth;
                if (i > 0) {
                    renderer.text(
                        priority_total,
                            cellLeft - cellPadding,
                            tableTop + (data[1].length + 3) * rowHeight - cellPadding
                    )
                        .attr({
                            align: 'center'
                        })
                        .css({
                            //fontWeight: 'bold',
                            //fontSize: '10pt',
                            font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
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
                            //fontWeight: 'bold',
                            //fontSize: '10pt',
                            font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                        })
                        .add();
                }

            });
            /*
             cellLeft = tableLeft + 25;
             $.each(row_label, function(i, item) {
             cellLeft += colWidth;
             // vertical lines
             if (i == 0) { // left table border
             Highcharts.tableLine(
             renderer,
             tableLeft,
             tableTop + cellPadding,
             tableLeft,
             tableTop + (data[1].length + 1) * rowHeight + cellPadding
             );
             }

             Highcharts.tableLine(
             renderer,
             cellLeft,
             tableTop + cellPadding,
             cellLeft,
             tableTop + (data[1].length + 1) * rowHeight + cellPadding
             );

             if (i == row_label.length - 1) { // right table border

             Highcharts.tableLine(
             renderer,
             cellLeft + colWidth + 35,
             tableTop + cellPadding,
             cellLeft + colWidth + 35,
             tableTop + (data[1].length + 1) * rowHeight + cellPadding
             );
             }
             })
             */
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
        var pie_title, color_title, uat_title;
        if (uat_type == 'include_uat' || uat_type == 'exclude_uat') {
            pie_title = 'Component Distribution';
        } else if (uat_type == 'only_uat') {
            uat_title = 'UAT';
        } else if (uat_type == 'custom') {
            if (uat_type_custom == 'exclude_uat') {
                uat_title = 'Custom Internal Testing';
            } else {
                uat_title = 'Custom UAT';
            }
        }
        if (uat_type == 'only_uat' || uat_type == 'custom') {
            if ( parseFloat(data[3]) > 10) {
                if (parseFloat(data[3]) == 103 ){
                    pie_title = 'No Open Issues';
                } else {
                    pie_title = 'CEEQ Score: ' + 'Out of Range';
                }
            }
            else {
                pie_title = '<b>{{ project.name }} - </b>'
                    //+ 'CEEQ Score - '
                    + uat_title
                    + ': '
                    + parseFloat(data[3]).toFixed(2)
                    + ' / 10';
            }
        }

        if ( parseFloat(data[3]) < 0) {
            color_title = '#FF0000';
        }
        else {
            color_title = '#000000';
        }

        var
        //colors = ['#CC6600', '#00CCCC', '#CCCC00', '#000066', '#990099', '#006600'],
        //scheme #5
            //colors = ['#9C775C', '#7D7D7D', '#3C7DC4', '#AD8B3B', '#0C2C52', '#4F193A'],
        //scheme #6
            //colors = ['#AD7C1F', '#FF8F00', '#1E8F9C', '#3B73A1', '#23635A', '#173096'],
        //scheme #6 change sequence
            colors = ['#23635A', '#FF8F00', '#1E8F9C', '#3B73A1', '#AD7C1F', '#173096'],
            componentData = [],
            subcomData = [],
            i,
            j,
            innerData = data[0][0],
            outerData = data[0][1],
            dataLen = innerData.length,
            drillDataLen,
            brightness;

        // Build the data arrays

        for (i = 0; i < dataLen; i += 1) {
            // add component data
            componentData.push({
                name: innerData[i][0],
                y: parseFloat(innerData[i][1]),
                color: colors[innerData[i][2]]
            });

            // add sub component data
            drillDataLen = outerData[i].length;
            for (j = 0; j < drillDataLen; j += 1) {
                brightness = 0.2 - (j / drillDataLen) / 5;
                subcomData.push({
                    name: outerData[i][j][0],
                    y: parseFloat(outerData[i][j][1]),
                    color: Highcharts.Color(colors[innerData[i][2]]).brighten(brightness).get()
                });
            }
        }

        var pie_size = 210;
        var chart_export = new Highcharts.Chart({
            chart: {
                //plotBackgroundColor: null,
                //plotBorderWidth: null,
                //plotShadow: false,
                renderTo: pie_chart_id + uat_type,
                type: 'pie',
                events: {
                    //load: Highcharts.drawTable
                },
                style: {
                    fontFamily: 'serif'
                },
                borderWidth: 0
            },
            title: {
                text: pie_title,
                style: {
                    //fontSize: '18pt',
                    //color: color_title,
                    font: '15pt "Lucida Grande", Helvetica, Arial, sans-serif'
                },
                align: 'left'
            },
            tooltip: {
                //pointFormat: '{series.name}: <b>{point.percentage:.2f}%</b>'
                formatter: function () {
                    return this.point.name + ": <b>" + this.point.percentage.toFixed(2) + "%</b>";
                },
                style: {
                    font: '10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                }
            },
            plotOptions: {
                pie: {
                    //allowPointSelect: true,
                    cursor: 'pointer',
                    center: ['50%', 100],
                    size: pie_size
                }
            },
            series: [
                {
                    //type: 'pie',
                    name: 'Component Contribution',
                    point: {
                        events: {
                            click: function (e) {
                                //data[3][0] - Jira name, data[3][1] - is_superuser
                                //if (e.point.name=='Application' && data[3][0]=='VISI' && data[3][1]==true){
                                //if (e.point.name != 'Voice Slots') {
                                    //location.href = e.point.name;
                                    location.href = 'sub/' +'?component_type=' + e.point.name +'&uat_type='+ uat_type + '&start=' + startDatetime.format('X') + "&end=" + endDatetime.format('X') + "&uat_type_custom=" + uat_type_custom;
                                    e.preventDefault();
                                //}
                            }
                        }
                    },
                    size: pie_size * 0.85,
                    dataLabels: {
                        formatter: function () {
                            return this.point.percentage > 0 ? this.point.name : null;
                        },
                        style: {
                            font: '10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                        },
                        color: 'white',
                        distance: -50
                    },
                    data: componentData
                },
                {
                    name: 'Sub component',
                    data: subcomData,
                    size: pie_size,
                    innerSize: pie_size * 0.78,
                    dataLabels: {
                        formatter: function () {
                            //display only if large than XXX
                            return this.point.percentage > 0 ? this.point.name + ': ' + this.point.percentage.toFixed(2) + '%' : null;
                        },
                        style: {
                            font: '10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                        }
                    }
                }
            ],
            navigation: {
                buttonOptions: {
                    enabled: false
                }
            },
            credits: {
                enabled: false
            }
        });

        //button handler

        //$('#pdf_' + uat_type).click(function () {
        //    var chart = $(pie_chart_id + uat_type).highcharts();
        //    chart.exportChart({
        //        type: 'application/pdf',
        //        scale: 1,
        //        width: 550,
        //        filename: export_filename
        //    });
        //});
        //$('#jpeg_' + uat_type).click(function () {
        //    var chart = $(pie_chart_id + uat_type).highcharts();
        //    chart.exportChart({
        //        type: 'image/jpeg',
        //        scale: 1,
        //        filename: export_filename
        //    });
        //});
        //$('#png_' + uat_type).click(function () {
        //    var chart = $(pie_chart_id + uat_type).highcharts();
        //    chart.exportChart({
        //        type: 'image/png',
        //        scale: 1,
        //        //sourceWidth: 1000,
        //        //sourceHeight: 300,
        //        filename: export_filename
        //    });
        //});

        return chart_export;

    }
}

function displayQEIlogo(uat_type) {

    var pie_title, uat_title;
    if (uat_type == 'include_uat') {
        uat_title = 'Overall';
    } else if (uat_type == 'exclude_uat') {
        uat_title = 'Internal Testing';
    } else if (uat_type == 'only_uat') {
        uat_title = 'UAT';
    } else if (uat_type == 'custom') {
        if (uat_type_custom == 'exclude_uat') {
            uat_title = 'Custom Internal Testing';
        } else {
            uat_title = 'Custom UAT';
        }
    }
    pie_title = '<b>'
        +'{{project.name}}'.replace(/&amp;/g, '&')
        +' - </b>'
        + uat_title
        + ': 10 / 10';

    $('#qei_log_' + uat_type).highcharts({
        chart: {
            background: 'white',
            borderWidth: 0
        },
        title: {
            text: pie_title,
            style: {
                font: '18pt "Lucida Grande", Helvetica, Arial, sans-serif'
            },
            align: 'center'
        },
        navigation: {
            buttonOptions: {
                enabled: false
            }
        },
        credits: false
    }, function(chart) {
//        chart.renderer.image('http://apps.qaci01.wic.west.com/static/common/QEIPowerQ.png', 100, 80, 200, 200)
//            .add();
        chart.renderer.image('https://lh4.googleusercontent.com/-lrM9yKFyk5s/VPCN3p_9NRI/AAAAAAAAGIU/4Eid6EHuId8/s426/QEIPowerQ.png', 100, 80, 200, 200)
            .add();
    });

    //export button handler
    $('#pdf_qei_log_' + uat_type).click(function () {
        var chart = $('#qei_log_' + uat_type).highcharts();
        chart.exportChart({
            type: 'application/pdf',
            scale: 1,
            filename: export_filename
        });
    });
    $('#jpeg_qei_log_' + uat_type).click(function () {
        var chart = $('#qei_log_' + uat_type).highcharts();
        chart.exportChart({
            type: 'image/jpeg',
            scale: 1,
            filename: export_filename
        });
    });
    $('#png_qei_log_' + uat_type).click(function () {
        var chart = $('#qei_log_' + uat_type).highcharts();
        chart.exportChart({
            type: 'image/png',
            scale: 1,
            //sourceWidth: 1000,
            //sourceHeight: 300,
            filename: export_filename
        });
    });
}

function displayCeeqTrend(data, uat_type, trend_chart_id, title_score) {
    var pie_title, uat_title, color_title, y_min_value = 0;
    if (uat_type == 'include_uat') {
        uat_title = 'Overall';
    } else if (uat_type == 'exclude_uat') {
        uat_title = 'Internal Testing';
    } else if (uat_type == 'only_uat') {
        uat_title = 'UAT';
    } else if (uat_type == 'custom') {
        if (uat_type_custom == 'exclude_uat') {
            uat_title = 'Custom Internal Testing';
        } else {
            uat_title = 'Custom UAT';
        }
    }
    pie_title = '<b>'
        +'{{ project.name }}'.replace(/&amp;/g, '&')
        + ' - </b>'
        + uat_title
        + ': '
        + parseFloat(title_score).toFixed(2)
        + ' / 10';

    if ( parseFloat(title_score) < 0) {
        color_title = '#FF0000';
        y_min_value = -10;
    }
    else {
        color_title = '#000000';
    }

    trend_chart_id = trend_chart_id.substring(1, trend_chart_id.length);

    var chart_export = new Highcharts.Chart({
        chart: {
            renderTo: trend_chart_id + uat_type
        },
        title: {
            text: pie_title,
            style: {
                color: color_title,
                font: '18pt "Lucida Grande", Helvetica, Arial, sans-serif'
            },
            align: 'left'
        },
        subtitle: {
            text: 'CEEQ Score Trend Graph, ' + 'Affected Version: ' + '{{project.jira_version}}',
            x: -20
        },
        xAxis: {
            title: {
                text: 'Timeline'
            },
            categories: data['categories'],
            labels: {
                //only display month-day in xAxis label
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
                text: 'CEEQ Score'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }],
            max: 10,
            min: y_min_value
        },
        tooltip: {
            //formatter: function(){
            //    var s = '<b>' + this.x + '</b><br/>';
            //    s += this.series.name + ': <b>' + this.y + '</b>';
            //    return s;
            //}

            //pointFormat:'{series.name}: <b>{point.y}</b><br>',
            formatter:function(){
                var s = '<b>' + this.x + '</b>';
                $.each(this.points, function(){
                    s += '<br/>' + this.series.name + ': <b>' + this.y + '</b>';
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
                marker: {
                    enabled: false
                }
            }
        },
        series: [
            {
                name: 'Projected',
                data: data['ceeq_closed'],
                // maroon: 993232, green: 27ae60, blue: 397fdb
                color: '#993232'
            },
            {
                name: 'Actual',
                data: data['ceeq'],
                color: '#27ae60'
            }
        ],
        credits: false
    });

    // export button handler
    //$('#pdf_' + trend_chart_id.substring(1, 12) + uat_type).click(function(){
    //    var chart = $(trend_chart_id + uat_type).highcharts();
    //    chart.exportChart({
    //        type: 'application/pdf',
    //        scale: 1,
    //        width: 550,
    //        filename: export_trend_filename
    //    })
    //});
    //$('#jpeg_' + trend_chart_id.substring(1, 12) + uat_type).click(function(){
    //    var chart = $(trend_chart_id + uat_type).highcharts();
    //    chart.exportChart({
    //        type: 'image/jpeg',
    //        scale: 1,
    //        filename: export_trend_filename
    //    })
    //});
    //$('#png_' + trend_chart_id.substring(1, 12) + uat_type).click(function(){
    //    var chart = $(trend_chart_id + uat_type).highcharts();
    //    chart.exportChart({
    //        type: 'image/png',
    //        scale: 1,
    //        filename: export_trend_filename
    //    })
    //});

    return chart_export;
}

/**
 * Create a global getSVG method that takes an array of charts as an argument
 */
Highcharts.getSVG = function(charts) {
    var svgArr = [],
        top = 0,
        width = 0;

    $.each(charts, function(i, chart) {
        // check if chart is not undefined
        if ( null == chart) {
            return true;
        }

        var svg = chart.getSVG();
        svg = svg.replace('<svg', '<g transform="translate(0,' + top + ')" ');
        svg = svg.replace('</svg>', '</g>');

        top += chart.chartHeight;
        width = Math.max(width, chart.chartWidth);

        svgArr.push(svg);
    });

    return '<svg height="'+ top +'" width="' + width + '" version="1.1" xmlns="http://www.w3.org/2000/svg">' + svgArr.join('') + '</svg>';
};

/**
 * Create a global exportCharts method that takes an array of charts as an argument,
 * and exporting options as the second argument
 */
Highcharts.exportCharts = function(charts, options) {
    var form,
        svg = Highcharts.getSVG(charts);

    // merge the options
    options = Highcharts.merge(Highcharts.getOptions().exporting, options);

    // create the form
    form = Highcharts.createElement('form', {
        method: 'post',
        action: options.url
    }, {
        display: 'none'
    }, document.body);

    // add the values
    Highcharts.each(['filename', 'type', 'width', 'svg'], function(name) {
        Highcharts.createElement('input', {
            type: 'hidden',
            name: name,
            value: {
                filename: options.filename || 'chart',
                type: options.type,
                width: options.width,
                svg: svg
            }[name]
        }, null, form);
    });
    //console.log(svg); return;
    // submit
    form.submit();

    // clean up
    form.parentNode.removeChild(form);
};


function exportAllCharts(charts, donut_pie){
    var options_png = {
        'filename': export_filename,
        'type': 'image/png',
        },
        options_jpeg = {
        'filename': export_filename,
        'type': 'image/jpeg'
        },
        options_pdf = {
        'filename': export_filename,
        'type': 'application/pdf'
        },
        _charts;

    if (donut_pie == 'exclude_uat' || donut_pie == 'include_uat') {
        $('#png_export_all_' + donut_pie).click(function(){
            if (! $('#graph_select_' + donut_pie).prop('checked')){
                _charts = charts.slice(0, -1);
            } else {
                _charts = charts
            }
            Highcharts.exportCharts(_charts, options_png);
        });
        $('#jpeg_export_all_' + donut_pie).click(function(){
            if (! $('#graph_select_' + donut_pie).prop('checked')){
                _charts = charts.slice(0, -1);
            } else {
                _charts = charts
            }
            Highcharts.exportCharts(_charts, options_jpeg);
        });
        $('#pdf_export_all_' + donut_pie).click(function(){
            if (! $('#graph_select_' + donut_pie).prop('checked')){
                _charts = charts.slice(0, -1);
            } else {
                _charts = charts
            }
            Highcharts.exportCharts(_charts, options_pdf);
        });
    } else {
        $('#png_' + donut_pie).click(function(){
            Highcharts.exportCharts(charts, options_png);
        });
        $('#jpeg_' + donut_pie).click(function(){
            Highcharts.exportCharts(charts, options_jpeg);
        });
        $('#pdf_' + donut_pie).click(function(){
            Highcharts.exportCharts(charts, options_pdf);
        });
    }
}


function displayJiraDataTable(data, uat_type, jira_data_table_id) {
    jira_data_table_id = jira_data_table_id.substring(1, jira_data_table_id.length);
    var score = data[3];

    if (score < 10) {
        //Create the data table
        Highcharts.drawTable = function () {

            // user options
            var row_label = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial', 'Subtotal'];
            var row_orc_label = ['O', 'R', 'C',
                'O', 'R', 'C',
                'O', 'R', 'C',
                'O', 'R', 'C',
                'O', 'R', 'C'
            ];
            var tableTop = 50,
                colWidth = 30,
                tableLeft = 25,
                rowHeight = 25,
                cellPadding = 2.5,
                valueDecimals = 3;

            // internal variables
            var chart = this,
                renderer = chart.renderer,
                cellLeft = tableLeft;

            // draw components lables
            $.each(data[1], function (i, item) {
                renderer.text(
                    item[0],
                        cellLeft + cellPadding,
                        tableTop + (i + 3) * rowHeight - cellPadding
                )
                    .css({
                        //fontWeight: 'bold',
                        //fontSize: '10pt',
                        font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'

                    })
                    .add();
            });

            // draw jira priority lables
            cellLeft += colWidth;
            $.each(row_label, function (i, item) {
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
                        //fontWeight: 'bold',
                        //fontSize: '10pt',
                        font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
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
            $.each(row_orc_label, function (i, item) {
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
                        //fontStyle: 'italic',
                        //fontSize: '10pt',
                        color: 'blue',
                        font: 'bold italic 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                    })
                    .add();
            });

            $.each(data[1], function (row, item) {
                cellLeft = tableLeft + colWidth * 2;

                // apply number of jiras
                $.each(item, function (i, priority) {
                    cellLeft += colWidth;
                    if (i > 0) {
                        renderer.text(
                            priority,
                                cellLeft - cellPadding,
                                tableTop + (row + 3) * rowHeight - cellPadding
                        )
                            .attr({
                                align: 'center'
                            })
                            .css({
                                //fontSize: '10pt'
                                font: '10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                            })
                            .add();
                    }
                });

                if (row == 0) {
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
            $.each(data[2], function (i, priority_total) {
                cellLeft += colWidth;
                if (i > 0) {
                    renderer.text(
                        priority_total,
                            cellLeft - cellPadding,
                            tableTop + (data[1].length + 3) * rowHeight - cellPadding
                    )
                        .attr({
                            align: 'center'
                        })
                        .css({
                            //fontWeight: 'bold',
                            //fontSize: '10pt',
                            font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
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
                            //fontWeight: 'bold',
                            //fontSize: '10pt',
                            font: 'bold 10pt "Lucida Grande", Helvetica, Arial, sans-serif'
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
        var pie_title = 'JIRA Tickets Per SubComponent';

        var chart_export = new Highcharts.Chart({
            chart: {
                //plotBackgroundColor: null,
                //plotBorderWidth: null,
                //plotShadow: false,
                renderTo: jira_data_table_id + uat_type,
                type: 'pie',
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
                    //fontSize: '18pt',
                    //color: color_title,
                    font: '15pt "Lucida Grande", Helvetica, Arial, sans-serif'
                },
                align: 'left'
            },
            tooltip: {
                style: {
                    font: '10pt "Lucida Grande", Helvetica, Arial, sans-serif'
                }
            },
            plotOptions: {

            },
            series: [

            ],
            navigation: {
                buttonOptions: {
                    enabled: false
                }
            },
            credits: {
                enabled: false
            }
        });

        return chart_export;

    }

}