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

# 1-open, 3-In progress, 4-reopen, 5-resolved, 10001-UAT testing, 10003-Discovery
issue_status = ['1', '3', '4', '5', '10001', '10003']