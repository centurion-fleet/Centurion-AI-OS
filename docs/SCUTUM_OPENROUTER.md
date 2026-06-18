# Project Scutum — OpenRouter Enterprise (manual)

Adrian owns the OpenRouter Enterprise application (C1).

## Week 1 fallback

Until Enterprise EA is approved, set on the **website** Vercel project:

```bash
OPENROUTER_MASTER_KEY=sk-or-v1-...   # standard OpenRouter master key
```

When unset, `lib/subscriptions/openrouter.ts` generates locally hashed dev keys
so subscribe → account key → `centurion setup` works in staging without OR EA.

## Production

1. Apply at https://openrouter.ai/enterprise
2. Set `OPENROUTER_MASTER_KEY` in Vercel + rotate per-customer keys via `POST /keys`
3. Optional: Stripe vars `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_BILLING_PORTAL_URL`
