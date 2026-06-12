# Centurion OS — v0.16.0 Release Note

## @latest Pointer System — Authoritative Document Versioning

**Every Centurion now reads the current version of every tracked document. Always.**

### The Problem
Centurions wake fresh each session. Without persistent memory, a Centurion has no way to know whether the document it just read is the latest version or a stale copy. This caused confusion — old business plans being referenced, archived files mistaken for current ones, and version mismatches across the fleet.

### The Solution
A filesystem-level document versioning system built into Centurion OS core. Every tracked document resolves through a `@latest` pointer — a tiny JSON pointer file that maps the logical document name to its current physical path, checksum, and version number.

### Architecture

```
~/.centurion/docs/
├── centurion-business-plan@latest.md   ← Current version (always read this)
├── archive/                            ← All previous versions
│   └── centurion-business-plan-v1-20260612-090800.md
├── latest/
│   └── centurion-business-plan.pointer.json  ← @latest pointer
├── v1/                                 ← Versioned copies (optional)
├── v2/
└── changelog.json                      ← Append-only version history
```

### How It Works

| Operation | What Happens |
|-----------|-------------|
| **Read** | Resolve `name@latest` through pointer → get current file + checksum |
| **Publish** | Archive old → write new `{name}@latest.md` → update pointer → log changelog |
| **Status** | Show version, path, checksum, line count, author, summary |
| **Verify** | Confirm pointer checksum matches actual file on disk |
| **History** | Query the append-only changelog by document name |

### CLI Commands

```bash
# Read the latest version
python3 -m centurion doc read centurion-business-plan

# Publish a new version
python3 -m centurion doc publish centurion-business-plan \
  --file /path/to/new-version.md \
  --author "Titus" \
  --summary "Updated pricing to £7,495"

# Check what version is current
python3 -m centurion doc status centurion-business-plan

# Verify integrity
python3 -m centurion doc verify centurion-business-plan

# View publication history
python3 -m centurion doc history centurion-business-plan

# List all tracked documents
python3 -m centurion doc list
```

### File Header

Every `@latest` file carries an embedded metadata header so a Centurion can identify the version without consulting the pointer file:

```yaml
---
name: centurion-business-plan
version: 3
published: 2026-06-12T09:08:00Z
published_by: Titus
---
```

### Fleet Protocol

Before acting on any tracked document, a Centurion SHOULD:

1. Call `doc verify <name>` to confirm local integrity
2. Check the fleet-wide expected checksum (if available)
3. If mismatch detected — `doc publish` the corrected version

### First Document Published

The new business plan (June 12, 2026 — 489 lines, Slow Burn £7,495 / Rapid Expansion £4,995) has been published as `centurion-business-plan@latest.md` (v1).

### Files Added

| File | Purpose |
|------|---------|
| `centurion/docs/__init__.py` | Module exports |
| `centurion/docs/pointer.py` | Pointer file resolution, path conventions, checksums |
| `centurion/docs/manager.py` | DocumentManager: read, publish, archive, status, verify |
| `centurion/docs/changelog.py` | Append-only version history log |
| `centurion/__main__.py` | CLI commands (doc read/publish/status/history/list/verify) |

### Branch

`centurions/titus` — commit `749213fcb`
