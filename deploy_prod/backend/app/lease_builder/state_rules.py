# backend/app/lease_builder/state_rules.py
"""
Rules/checklists for lease drafting. This is NOT legal advice.
Use as a drafting assistant + checklist; confirm with an attorney for each jurisdiction.
"""

STATE_RULES = {
    "MN": {
        "state_name": "Minnesota",
        "required_disclosures": [
            {
                "key": "manager_address",
                "title": "Manager/agent + service of process address must be disclosed in writing",
                "note": "MN requires disclosure of who manages the premises + who can accept notices/service.",
                "source": "MN Stat. § 504B.181",
            },
            {
                "key": "lead_paint_pre_1978",
                "title": "Lead-based paint disclosure for pre-1978 housing (federal)",
                "note": "Federal rule applies to most pre-1978 housing; provide EPA pamphlet + known info.",
                "source": "EPA/HUD lead disclosure rule",
            },
        ],
        "default_clauses": [
            {"key": "late_fee", "title": "Late fee + grace period"},
            {"key": "utilities", "title": "Utilities responsibility"},
            {"key": "maintenance", "title": "Maintenance + reporting"},
            {"key": "entry_notice", "title": "Landlord entry notice"},
            {"key": "smoking", "title": "No smoking / smoking policy"},
            {"key": "pets", "title": "Pets addendum"},
            {"key": "subletting", "title": "Subletting policy"},
            {"key": "renters_insurance", "title": "Renter’s insurance requirement"},
            {"key": "parking", "title": "Parking rules"},
        ],
    },
    "DEFAULT": {
        "state_name": "Generic",
        "required_disclosures": [],
        "default_clauses": [
            {"key": "late_fee", "title": "Late fee + grace period"},
            {"key": "utilities", "title": "Utilities responsibility"},
            {"key": "maintenance", "title": "Maintenance + reporting"},
            {"key": "entry_notice", "title": "Landlord entry notice"},
            {"key": "smoking", "title": "No smoking / smoking policy"},
            {"key": "pets", "title": "Pets addendum"},
            {"key": "subletting", "title": "Subletting policy"},
            {"key": "renters_insurance", "title": "Renter’s insurance requirement"},
            {"key": "parking", "title": "Parking rules"},
        ],
    },
}
