# Centurion OS — Full Audit

**Audit date:** 28 May 2026  
**Auditor:** Titus 🦅  
**Source:** CenturionAI-OS-v3 fork of Hermes Agent  
**Upstream:** Nous Research Hermes Agent (v16.2.6)

---

## 1. What's Already Done (Phases 1 & 2)

### Phase 1 — Surface Rebrand (104 files)
- Renamed `hermes_cli/` → `centurion_cli/` directory
- Updated entry points and package name in `pyproject.toml`
- Updated README
- **Did NOT** update internal import paths referencing `hermes_cli`

### Phase 2 — Constant/State Rebrand (789 files)
- Renamed files: `hermes_constants.py` → `centurion_constants.py`
- Renamed: `hermes_state.py` → `centurion_state.py`
- Renamed: `hermes_logging.py` → `centurion_logging.py`
- Renamed: `hermes_bootstrap.py` → `centurion_bootstrap.py`
- Renamed: `hermes_time.py` → `centurion_time.py`
- Updated env vars and home directory paths
- Updated SOME internal references (incomplete — many still use old names)

---

## 2. Current State: Partially Broken

The repo is in a state where it **cannot run cleanly**. The directory `hermes_cli/` was renamed to `centurion_cli/` but ~707 internal import statements still reference `hermes_cli`. These will produce `ModuleNotFoundError` at runtime.

### Import Breakage Counts

| Module | Old Name | New Name | Still Using Old | Category |
|--------|----------|----------|-----------------|----------|
| `hermes_cli.*` | `hermes_cli/` dir | `centurion_cli/` | **707** 🔴 | **BROKEN — dir renamed, imports not updated** |
| `hermes_constants` | `hermes_constants.py` | `centurion_constants.py` | 136 | 🟡 Inconsistent |
| `hermes_state` | `hermes_state.py` | `centurion_state.py` | 108 | 🟡 Inconsistent |
| `hermes_logging` | `hermes_logging.py` | `centurion_logging.py` | 92 | 🟡 Inconsistent |
| `hermes_bootstrap` | `hermes_bootstrap.py` | `centurion_bootstrap.py` | 27 | 🟡 Inconsistent |
| `hermes_time` | `hermes_time.py` | `centurion_time.py` | 37 | 🟡 Inconsistent |

**Total Python refactor surface:** ~1,107 lines across ~160 core files

### Other Remaining Surfaces

| Surface | Files Containing "hermes" | Priority |
|---------|--------------------------|----------|
| Website/docs (Docusaurus) | 588 | 🟢 Low — docs branding |
| Skills (built-in) | 107 | 🟡 Medium — affects user experience |
| Skills (optional) | 106 | 🟢 Low — user contributed |
| Language/translation files | 27 | 🟢 Low — cosmetic |
| GitHub config (CI, issues, PRs) | 14 | 🟡 Medium — CI will reference old name |
| Shell scripts | 13 | 🟡 Medium — install scripts |
| README files | 21 | 🟢 Low — docs branding |
| Plugin: `hermes-achievements` | 1 dir | 🟡 Medium — built-in plugin |
| Config files (yaml/toml/json) | 44 | 🟡 Medium — runtime config |

---

## 3. Categorised Findings

### 🔴 Critical — Blocks Runtime

1. **`hermes_cli` imports** (707 refs) — The directory was renamed but every `from hermes_cli.xxx import yyy` still points at the old name. These will all fail at import time.

2. **`pyproject.toml` deps** — Still lists `hermes-agent[cron]`, `hermes-agent[cli]`, `hermes-agent[pty]` as dependencies instead of `centurionai-os[...]`.

3. **CLI entry point** — The `hermes` shebang script at repo root still references `hermes` in its CLI name. Users would type `hermes` not `centurion`.

### 🟡 Medium — Works But Confusing

4. **Mixed naming** — Some files now use `centurion_*` imports while others still use `hermes_*`. E.g., `run_agent.py` imports from `centurion_constants` but `centurion_cli/main.py` imports from `hermes_cli.config`. Inconsistent.

5. **Function/variable names** — Internal functions like `get_hermes_home()`, `load_hermes_dotenv()` still carry "hermes" in their names even after the files were renamed. Creates confusion.

6. **Skills** — 107 built-in skill files reference `hermes` in their SKILL.md and scripts. The `hermes-agent` skill is particularly relevant since it's our current platform.

7. **i18n/locales** — 27 translation files (en.yaml, de.yaml, etc.) contain `hermes` in labels and strings.

8. **GitHub CI** — Workflow files in `.github/` reference `hermes` in job names, action names, and deploy targets.

### 🟢 Low — Cosmetic / Docs

9. **Website docs** (588 files) — The entire Docusaurus documentation site still uses the old naming. All URLs, headings, and code examples say "Hermes."

10. **README files** — 21 READMEs across the codebase still reference Hermes.

11. **Release notes** — `RELEASE_v*.md` files document Hermes history. These would be confusing under the Centurion brand.

---

## 4. What Phase 1 & 2 Actually Changed (Detailed)

### Files successfully renamed

```
hermes_constants.py     → centurion_constants.py ✓
hermes_state.py         → centurion_state.py     ✓
hermes_logging.py       → centurion_logging.py   ✓
hermes_bootstrap.py     → centurion_bootstrap.py ✓
hermes_time.py          → centurion_time.py      ✓
hermes_cli/             → centurion_cli/         ✓
```

### Internal refs that were updated (examples)
- `get_centurion_home()` — function was renamed in `centurion_constants.py`
- Some imports in `run_agent.py`, `model_tools.py` already use `centurion_*` prefix

### Internal refs that were NOT updated (examples)
- `centurion_cli/main.py` line 103: `from hermes_cli import __version__` — **BROKEN**
- `centurion_cli/main.py` line 273: `from hermes_cli.config import get_centurion_home` — **BROKEN**
- Throughout `agent/`, `gateway/`, `tools/`: hundreds of `from hermes_cli.*` imports — **BROKEN**
- `centurion_constants.py`: function `get_hermes_home()` still has "hermes" in name
- `centurion_bootstrap.py`: many internal references still say "hermes"

### What the phase commits touched
- **Phase 1** (`80407c21c`): 104 files — directory renames + README + pyproject
- **Phase 2** (`c92b7503d`): 789 files — mass rename of constants/state/bootstrap references + env vars
- **Phase 3 (this audit):** ~1,107 remaining Python references need updating

---

## 5. Design Decisions to Make

Before Phase 3 execution, these need answering:

1. **Package name** — `centos`? `centurion-os`? `centurionai-os`? Currently `centurionai-os` in pyproject. Confirm.

2. **CLI invocation** — `hermes` → `centurion`? Or keep `hermes` as an alias/symlink? Users type this constantly.

3. **Import rename strategy** — Mechanical sed/replace (fast, risky) or per-file refactor (safe, slow)?

4. **Skills compatibility** — Skills using `from hermes_tools import terminal` need to either (a) be updated to `from centurion_tools import ...` or (b) have a compatibility layer. If skills are installed from a registry, this affects external users.

5. **Docs branding** — Full rewrite or just search-and-replace on the Docusaurus site?

6. **Heritage tracking** — How do we reference the Hermes origin? Upstream merges will conflict if we rename everything.

---

## 6. Files Not Needing Change

Some "hermes" references are intentional and should be preserved:

- `hermes-already-has-routines.md` — A document that intentionally compares Hermes vs Centurion
- Heritage/attribution references in licenses
- Upstream changelogs and release notes
- `AGENTS.md` — references Hermes as the current runtime (factual, not branding)
