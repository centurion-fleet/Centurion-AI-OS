# Langfuse Observability Plugin

This plugin ships bundled with Centurion but is **opt-in** — it only loads when
you explicitly enable it.

## Enable

```bash
pip install langfuse
centurion plugins enable observability/langfuse
```

Or check the box in the interactive `centurion plugins` UI.

## Required credentials

Set these in `~/.centurion/.env`:

```bash
CENTURION_LANGFUSE_PUBLIC_KEY=pk-lf-...
CENTURION_LANGFUSE_SECRET_KEY=sk-lf-...
CENTURION_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

Without the SDK or credentials the hooks no-op silently — the plugin fails
open.

## Verify

```bash
centurion plugins list                 # observability/langfuse should show "enabled"
centurion chat -q "hello"              # then check Langfuse for a "Centurion turn" trace
```

## Optional tuning

```bash
CENTURION_LANGFUSE_ENV=production       # environment tag
CENTURION_LANGFUSE_RELEASE=v1.0.0       # release tag
CENTURION_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
CENTURION_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
CENTURION_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## Disable

```bash
centurion plugins disable observability/langfuse
```
