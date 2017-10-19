/**
 * Created by sliu on 4/18/16.
 */
// String format custom method
String.prototype.format = function () {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

// for projects project_detail to show/hide jira_key and query_field
$('.projectQueryField').on('change', function(evt){
    var key = '{{project.jira_key}}',
        class_name = this.className.split(' ')[2],
        location = '';

    if (class_name === 'projectEditQF'){
        location = '.editProject';
    } else {
        location = '.newProject'
    }

    if (this.value === 'JQL Query'){
        $('{0} label[for="id_jira_key"]'.format(location)).hide();
        $('{0} #id_jira_key'.format(location)).val('JQL');
        $('{0} label[for="id_jira_version"]'.format(location)).hide();
        $('{0} #id_jira_version'.format(location)).hide();
        $('{0} #id_jira_key'.format(location)).hide();
        $('{0} label[for="id_query_jql"]'.format(location)).show();
        $('{0} #id_query_jql'.format(location)).show();
    } else {
        $('{0} label[for="id_jira_key"]'.format(location)).show();
        $('{0} #id_jira_key'.format(location)).val(key);
        $('{0} #id_jira_key'.format(location)).show();
        $('{0} label[for="id_jira_version"]'.format(location)).show();
        $('{0} #id_jira_version'.format(location)).show();
        $('{0} label[for="id_query_jql"]'.format(location)).hide();
        $('{0} #id_query_jql'.format(location)).hide();
    }
});

function showErrMsg(location, msg) {
    $(location).css({
        'font-size': 15,
        'color': 'blue'
    });
    $(location).html('Error: ' + msg);
}