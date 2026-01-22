Promos:
- Only landlords subscribe (tenants never subscribe)
- Billing: per active billable unit per month
- Units have is_billable_active boolean; subscription quantity = count(true)
- Promos can be enabled/disabled at app level
- Prefer Stripe Promotion Codes for standard discounts; allow internal "comped_until" for sales
