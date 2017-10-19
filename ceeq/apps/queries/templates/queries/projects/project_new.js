$('#project-new-modal').on('shown.bs.modal', function () {
    var query_field = $('#project-new-modal #id_query_field').val();

    if (query_field === 'JQL Query'){
        $('#project-new-modal #id_jira_key').hide()
    }
});

$('#project-new-modal form').on('submit', function(event){
    var name = $('#id_name').val(),
        key = $('#id_jira_key').val(),
        query_field = $('#id_query_field').val(),
        query_jql = $('#id_query_jql').val();

    if (name == '') {
        showErrMsg('#newProjectErrMessage', 'Name is Empty');
        return false;
    }
    if ((query_field == 'Project Version') && (key == '')){
        showErrMsg('#newProjectErrMessage', 'Jira Key is Empty');
        return false;
    }
    if ((query_field == 'JQL Query') && (query_jql == '')){
        showErrMsg('#newProjectErrMessage', 'Query JQL is Empty');
        return false;
    }
});