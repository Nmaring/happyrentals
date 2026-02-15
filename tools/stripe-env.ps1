# --- Stripe config (local only, do not commit) ---
$env:STRIPE_SECRET_KEY="sk_test_..."              # <-- paste your Stripe secret key here
$env:STRIPE_WEBHOOK_SECRET="whsec_558f0aa8c8fb9e8595c5cb9e5b98ef248ab00e46693e9fd8134d784dc0e626d3"

# Prices (create these in Stripe Dashboard → Products → Prices)
$env:STRIPE_PRICE_PER_UNIT="price_..."           # <-- paste price id for per-unit monthly
$env:STRIPE_PRICE_PER_TENANT="price_..."         # <-- paste price id for per-tenant monthly (optional)
$env:STRIPE_PRICE_FLAT="price_..."               # <-- paste flat monthly (optional)
