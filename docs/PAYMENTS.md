Tenant payment options (target):
- Manual: Cash, Check, Venmo, Zelle, Bank transfer (recorded by landlord)
- Card + Wallets: via Stripe Payment Element (Apple Pay/Google Pay where available)
- ACH: via Stripe (US) where enabled
- Optional: PayPal/Venmo checkout via a separate provider (Phase 2)

Implementation: provider interface with:
processor: stripe|braintree|manual
method: card|ach|cash|check|venmo|zelle|bank_transfer|other
channel: online|manual
