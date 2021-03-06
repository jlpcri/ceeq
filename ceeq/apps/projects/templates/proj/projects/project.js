var framework_parameter_items = ['jira_issue_weight_sum',
                                       'vaf_ratio',
                                       'vaf_exp'];
var active_tab = String("");
var active_pill = String("");
var projects_last_active_pill = String("");

$('#subnav-tabs').find('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
    active_tab = e.target.hash;
    loadActiveDataTab();
});

$('#projects-pills').find('a[data-toggle="pill"]').on('show.bs.tab', function(e) {
    projects_last_active_pill = e.target.hash;
    active_pill = e.target.hash;
});

$(document).ready(function() {
    $('#subnav-tabs').find('a[href="#projects"]').tab('show');

});

function showThrobber() {
    $('#throbber').show();
}

function loadActiveDataTab() {

    if (active_tab == '#projects'){
        if (projects_last_active_pill == '#projects-archive') {
            $('#projects-pills').find('a[href="#projects-archive"]').tab('show');
        } else {
            $('#projects-pills').find('a[href="#projects-active"]').tab('show');
        }

        $('#update_all').click(function () {
            showThrobber();
        });
        $('#dd_log_all').click(function () {
            showThrobber();
        });
        $('*[id*=project_type]').each(function(){
            $(this).click(function(e){
                e.preventDefault();
                $('a[href="' + $(this).attr('href') + '"]').tab('show');
            });
        });

    }
    else if (active_tab == '#score_overall') {
        Highcharts.setOptions({
            //colors: ['#CC6600', '#00CCCC', '#CCCC00', '#000066', '#990099', '#006600']
            colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
            '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1',
            '#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce',
            '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'
        ]
        });
        $.getJSON("{% url 'projects:fetch_projects_score' %}").done(function(data){
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

            $('#score_container').highcharts({
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
                    min: min_yaxis,
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
                            x: 0,
                            y:-1,
                            formatter: function(){
                                return this.y.toFixed(2)
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
    }
    else if (active_tab == '#framework_parameter'){

        $("#new_parameter").autocomplete({
            source: framework_parameter_items,
            autoFocus: true,
            minLength: 0
        });

        $('#parameters_include').html('\'' + framework_parameter_items + '\'');

        $('#new_argument_submit').click(function() {
            var new_parameter = $('#new_parameter').val().trim();
            if ( new_parameter == ''){
                $('#new_argument_errors').text("parameter cannot be empty!");
            }
            else {
                if ( $('#new_value').val().trim() == '' ){
                    $('#new_argument_errors').text("value cannot be empty!");
                }
                else {
                    var new_value = $('#new_value').val().trim();
                    if (isNaN(new_value)){
                        $('#new_argument_errors').text("value value should be Numbers!");
                    }
                    else  {
                        new_argument = JSON.stringify({
                                parameter: new_parameter,
                                value: new_value
                                });
                        var button = $(this);
                        button.attr('disabled', 'disabled');
                        button.html("<i class='icon-spinner icon-spin'></i> ");
                        $.ajax({
                            url: "/ceeq/api/v1/argument/",
                            type: "POST",
                            contentType: "application/json",
                            dataType: 'json',
                            data: new_argument
                            }).complete(function(response) {
                                if (response.status == 201) {
                                    var argument_url = response.getResponseHeader('Location').toString();
                                    $.ajax({
                                        url: argument_url,
                                        type: "GET",
                                        dataType: 'json'
                                    }).complete(function(response) {
                                                argument = JSON.parse(response.responseText);
                                                insertArgument(argument);
                                    });
                                    button.removeAttr('disabled', 'disabled');
                                    button.html("Create");
                                    $('#new_parameter').val('').focus();
                                    $('#new_value').val('');
                                    $('#new_argument_errors').text("");
                                    $('html, body').animate({
                                        scrollTop: $("#new_parameter").offset().top
                                    }, 800);
                                }
                                else {
                                    response = JSON.parse(response.responseText);
                                    console.log(response.error_message)
                                    if (response.error_message == "column parameter is not unique") {
                                        $('#new_argument_errors').text("parameter \"" + new_parameter + "\" is not unique!");
                                        $('#new_parameter').focus().select();
                                        button.removeAttr('disabled', 'disabled');
                                        button.html("Create");
                                        $('#argument_table > tbody > tr').each(function() {
                                            if ($(this).find('.parameter').val()) {
                                                if ($(this).find('.parameter').val() == new_parameter) {
                                                    var row = $(this);
                                                    row.css('-webkit-transition','background-color 0s');
                                                    row.css('background-color','rgba(227, 118, 114, 1.0)');
                                                    setTimeout(function() {
                                                        row.css('-webkit-transition','background-color 1s');
                                                        row.css('background-color','rgba(255, 255, 255, 0.47)');
                                                    }, 500);
                                                }
                                            }
                                        });
                                    }
                                }
                        });
                    }
                }
            }
        });

        $('#argument_table').on('click', '.argument-delete', function(event) {
            var row = $(this).closest('tr');
            var argument_id = row.attr('id');
            var button = row.find('.argument-delete');
            button.html("<i class='icon-spinner icon-spin icon-large'></i>");
            button.attr('disabled', 'disabled');
            $.ajax({
                url: "/ceeq/api/v1/argument/" + argument_id +"/",
                method: 'DELETE'
            }).done(function(data) {
                row.remove();
            });
            location.reload();
        });

        $('#argument_table').on('click', '.argument-save', function(event) {
            var row = $(this).closest('tr');
            var argument_id = row.attr('id');
            var button = row.find('.argument-save');
            var parameter = row.find('.parameter').val().trim();
            <!-- console.log(parameter) -->
            if ( parameter == '') {
                row.find('.errors').text("parameter cannot be empty!");
            }
            else {
                if (row.find('.value').val().trim() == '') {
                    row.find('.errors').text("value cannot be empty!");
                }
                else {
                    var value = row.find('.value').val().trim();
                    if (isNaN(value)) {
                        row.find('.errors').text("value value should be Numbers!");
                    }
                    else {
                        button.html("<i class='icon-spinner icon-spin icon-large'></i>");
                        button.attr('disabled', 'disabled');
                        data = JSON.stringify({
                                parameter: parameter,
                                value: value
                                })
                        $.ajax({
                            url: "/ceeq/api/v1/argument/" + argument_id +"/",
                            method: 'PUT',
                            contentType: "application/json",
                            dataType: 'json',
                            data: data
                        }).complete(function(response) {
                            if (response.status == 204) {
                                row.find('.parameter').val(parameter);
                                row.find('.value').val(value);
                                row.find('.errors').text("Saved!");
                                button.removeAttr('disabled', 'disabled');
                                button.html("Update");
                                row.css('-webkit-transition','background-color 0s');
                                row.css('background-color','rgba(173, 216, 230, 0.47)');
                                setTimeout(function() {
                                    row.css('-webkit-transition','background-color 1s');
                                    row.css('background-color','rgba(255, 255, 255, 0.47)');
                                    row.find('.errors').text("");
                                }, 1000);
                            }
                            else {
                                response = JSON.parse(response.responseText);
                                if (response.error_message == "columns project_id, parameter are not unique") {
                                    row.find('.errors').text("parameter \"" + parameter + "\" is not unique!");
                                    button.removeAttr('disabled', 'disabled');
                                    button.html("Update");
                                    $('#argument_table > tbody > tr').each(function() {
                                        if ($(this).find('.parameter').val()) {
                                            if ($(this).find('.parameter').val() == parameter) {
                                                var row = $(this);
                                                row.css('-webkit-transition','background-color 0s');
                                                row.css('background-color','rgba(227, 118, 114, 1.0)');
                                                setTimeout(function() {
                                                    row.css('-webkit-transition','background-color 1s');
                                                    row.css('background-color','rgba(255, 255, 255, 0.47)');
                                                }, 500);
                                            }
                                        }
                                    });
                                }
                            }
                        });
                        setTimeout(function() {
                            location.reload();
                        }, 3000);
                    }
                }
            }
        });

        function insertArgument (argument) {
            $('#argument_table > tbody > tr').each(function() {
                if ($(this).find('.parameter').val()) {
                    if ($(this).find('.parameter').val() > argument.parameter) {
                        $(this).before("<tr id=\"" + argument.id + "\" class=\"added-argument\"><td class=\"col-sm-3\"><input type=\"text\" class=\"form-control parameter\" value=\"" + argument.parameter + "\" onkeypress=\"clickSave(event);\"></td><td class=\"col-sm-3\"><input type=\"text\" class=\"form-control value\" value=\"" + argument.value + "\" onkeypress=\"clickSave(event);\"></td><td class=\"col-sm-3 errors\"><span class=\"errors\"></span></td><td class=\"col-sm-2\"><button class=\"btn btn-block btn-primary argument-save\">Update</button></td><td class=\"col-sm-1\"><button class=\"btn btn-block btn-danger argument-delete\"><i class=\"fa fa-trash-o\"></i></button></td></tr>")
                        return false;
                    }
                }
                else if ($(this).hasClass('new-argument')) {
                    $(this).before("<tr id=\"" + argument.id + "\" class=\"added-argument\"><td class=\"col-sm-3\"><input type=\"text\" class=\"form-control parameter\" value=\"" + argument.parameter + "\" onkeypress=\"clickSave(event);\"></td><td class=\"col-sm-3\"><input type=\"text\" class=\"form-control value\" value=\"" + argument.value + "\" onkeypress=\"clickSave(event);\"></td><td class=\"col-sm-3 errors\"><span class=\"errors\"></span></td><td class=\"col-sm-2\"><button class=\"btn btn-block btn-primary argument-save\">Update</button></td><td class=\"col-sm-1\"><button class=\"btn btn-block btn-danger argument-delete\"><i class=\"fa fa-trash-o\"></i></button></td></tr>")
                }
            });
            $('#argument_table > tbody > tr').each(function() {
                if ($(this).hasClass('added-argument')) {
                    var row = $(this);
                    row.css('-webkit-transition','background-color 0s');
                    row.css('background-color','rgba(173, 216, 230, 0.47)');
                    setTimeout(function() {
                        row.css('-webkit-transition','background-color 1s');
                        row.css('background-color','rgba(255, 255, 255, 0.47)');
                    }, 500);
                    row.removeClass('added-argument');
                }
            });
            location.reload();
        }

        $("#new_parameter").keypress(function(event){
            if(event.keyCode == 13){
                $("#new_argument_submit").focus();
            }
        });

        $("#new_value").keypress(function(event){
            if(event.keyCode == 13){
                $("#new_argument_submit").focus();
            }
        });

        function clickSave(event) {
            if (event.keyCode == 13) {
                var source = event.srcElement;
                var button = $(source).closest('tr').find('.argument-save');
                button.click();
            }
        }
    }
    else if (active_tab == '#defects_density_admin'){
        $.getJSON("{% url 'dds:fetch_dds_json' 1000000 %}").done(function(data) {
            $('#dd_list').html('<table cellpadding="0" cellspacing="0" border="0" class="display" id="dd_list_table"></table>');
            $('#dd_list_table').dataTable({
                "data":data,
                "columns": [
                    {"title": "Project"},
                    {"title": "Version"},
                    {"title": "Date"},
                    {"title": "CXP"},
                    {"title": "Platform"},
                    {"title": "Reports"},
                    {"title": "Application"},
                    {"title": "Prompts"},
                    {"title": "CEEQ"}
                ],
                "language": {
                    "decimal": ".",
                    "thousands": ","
                }
            });
        });

    }
}

