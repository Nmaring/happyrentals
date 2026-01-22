# backend/app/lease_builder/router.py
from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.lease_builder.state_rules import STATE_RULES

router = APIRouter(prefix="/lease-builder", tags=["lease-builder"])

class LeaseDraftRequest(BaseModel):
    state: str = Field(default="MN", min_length=2, max_length=2)
    lease_type: str = "fixed_term"  # fixed_term | month_to_month | open_ended
    term_months: Optional[int] = 12
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None

    landlord_name: str = "LANDLORD NAME"
    tenant_name: str = "TENANT NAME"
    property_address: str = "PROPERTY ADDRESS"
    unit_label: str = "UNIT"

    monthly_rent: float = 0
    rent_due_day: int = 1
    security_deposit: float = 0

    clauses: Dict[str, Any] = Field(default_factory=dict)

@router.get("/rules/{state_code}")
def rules(state_code: str):
    s = state_code.upper()
    return STATE_RULES.get(s) or STATE_RULES["DEFAULT"]

@router.post("/render")
def render(req: LeaseDraftRequest):
    ruleset = STATE_RULES.get(req.state.upper()) or STATE_RULES["DEFAULT"]

    lines = []
    lines.append(f"# Residential Lease Draft ({ruleset.get('state_name','')})")
    lines.append("")
    lines.append("**NOT LEGAL ADVICE.** This is a drafting checklist. Review with a qualified attorney.")
    lines.append("")
    lines.append(f"**Landlord:** {req.landlord_name}")
    lines.append(f"**Tenant:** {req.tenant_name}")
    lines.append(f"**Premises:** {req.property_address} — {req.unit_label}")
    lines.append("")
    lines.append(f"**Lease type:** {req.lease_type}")
    lines.append(f"**Start date:** {req.start_date.isoformat()}")
    if req.end_date:
        lines.append(f"**End date:** {req.end_date.isoformat()}")
    elif req.lease_type == "fixed_term":
        lines.append(f"**End date:** (auto) {req.start_date.isoformat()} + {req.term_months or 12} months")
    else:
        lines.append("**End date:** N/A")
    lines.append("")
    lines.append(f"**Monthly rent:** ${req.monthly_rent:,.2f}")
    lines.append(f"**Rent due day:** {req.rent_due_day}")
    lines.append(f"**Security deposit:** ${req.security_deposit:,.2f}")
    lines.append("")
    lines.append("## Disclosures & Checklists")
    if ruleset.get("required_disclosures"):
        for item in ruleset["required_disclosures"]:
            lines.append(f"- [ ] {item['title']}  _(Source: {item.get('source','')})_")
            if item.get("note"):
                lines.append(f"  - {item['note']}")
    else:
        lines.append("- (No state checklist configured yet.)")
    lines.append("")
    lines.append("## Clause Options (selected)")
    if req.clauses:
        for k, v in req.clauses.items():
            lines.append(f"- **{k}**: {v}")
    else:
        lines.append("- (None selected)")
    lines.append("")
    lines.append("## Signatures")
    lines.append("- Landlord: ____________________  Date: __________")
    lines.append("- Tenant: ______________________  Date: __________")

    return {"draft": "\n".join(lines)}
