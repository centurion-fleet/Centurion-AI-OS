# Shell=True audit (2026-06)

Tracked uses of `subprocess` / `Popen` with `shell=True` in production code paths.
Prefer explicit argv lists; keep `shell=True` only where documented below.

## Acceptable / intentional

| File | Rationale |
|------|-----------|
| `cli.py` | User-defined `quick_commands` — arbitrary shell snippets by design |
| `centurion_cli/_subprocess_compat.py` | Windows `.cmd` / PATHEXT fallback |
| `centurion_cli/tools_config.py` | User-triggered optional extra install command from config |
| `tools/environments/docker.py` | Docker stop/rm one-liners; candidates for argv split later |
| `tools/transcription_tools.py` | External media toolchain (ffmpeg-style); needs shell for pipes |

## Tests only

`tests/tools/*`, `tests/test_live_system_guard_self_test.py` — not production surfaces.

## Follow-up

- `tui_gateway/server.py` — evaluate argv form for editor/pager invocations
- `tools/environments/docker.py` — split stop/rm into list form when touching that module
