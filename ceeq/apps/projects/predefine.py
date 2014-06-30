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
    'blocker': Decimal(5) / 15,
    'critical': Decimal(4) / 15,
    'major': Decimal(3) / 15,
    'minor': Decimal(2) / 15,
    'trivial': Decimal(1) /15
}

# 1-open, 3-In progress, 4-reopen, 5-resolved, 10001-UAT testing, 10003-Discovery
issue_status = ['1', '3', '4', '5', '10001', '10003']