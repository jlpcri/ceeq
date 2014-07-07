# pre-define Standard Component Name and its comparison ratio
from decimal import Decimal

component_names_standard = {
    'CXP': 2,
    'Platform': 4,
    'Reports': 3,
    'Application': 8,
    'Voice Slots': 3,
}

# pre-define Priority Weight of Issues in JIRA
issue_priority_weight = {
    'blocker': Decimal(50) / 150,
    'critical': Decimal(40) / 150,
    'major': Decimal(30) / 150,
    'minor': Decimal(20) / 150,
    'trivial': Decimal(10) /150
}

# 1-open, 3-In progress, 4-reopen, 5-resolved, 6-closed, 10001-UAT testing, 10003-Discovery
issue_status_open = ['1', '3', '4', '10001', '10003']
#issue_status_in_progress = '3'
issue_status_resolved = ['5']
issue_status_closed = ['6']
#issue_status_uat_testing = '10001'
#issue_status_discovery = '10003'

# data structure for broken issue status
issue_status_count = {
    'open': 0,
    #'in_progress': 0,
    #'reopen': 0,
    'resolved': 0,
    'closed': 0,
    #'uat_testing': 0,
    #'discovery': 0
}

# issue status weight ratio
issue_status_weight = {
    'open': Decimal(7) / 10,
    #'in_progress': 0,
    #'reopen': 0,
    'resolved': Decimal(2) / 10,
    'closed': Decimal(1) / 10,
    #'uat_testing': 0,
    #'discovery': 0
}