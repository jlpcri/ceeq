/**
 * Created by sliu on 4/18/16.
 */

// for projects project_detail to show/hide jira_key and query_field
$('#id_query_field').on('change', function(){
    if (this.value == 'JQL Query'){
        $('label[for="id_jira_key"]').hide();
        $('#id_jira_key').val('JQL');
        $('label[for="id_jira_version"]').hide();
        $('#id_jira_version').hide();
        $('#id_jira_key').hide();
        $('label[for="id_query_jql"]').show();
        $('#id_query_jql').show();
    } else {
        $('label[for="id_jira_key"]').show();
        $('#id_jira_key').show();
        $('label[for="id_jira_version"]').show();
        $('#id_jira_version').show();
        $('label[for="id_query_jql"]').hide();
        $('#id_query_jql').hide();
    }
});