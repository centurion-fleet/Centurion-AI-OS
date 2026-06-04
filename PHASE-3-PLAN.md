# Phase 3 — Action Plan

**Goal:** Make Centurion-AI-OS-v4 runnable and consistently branded.  
**Based on:** CENTURION-OS-AUDIT.md findings  
**Strategy:** Fix in order of breakage — critical first, cosmetic last.

---

## Priority Order

### 🔴 P0 — Must Fix Before Anything Runs

These are actual runtime blockers. The repo cannot start until these are done.

- [ ] **P0.1 — Fix `hermes_cli` imports** (707 refs)
  - Bulk replace `from hermes_cli` → `from centurion_cli` in all `.py` files
  - Bulk replace `import hermes_cli` → `import centurion_cli`
  - Risk: `sed` is fast but may catch commented-out code or strings. Safer: targeted search per file.
  - After this, the internal module resolution should work.

- [ ] **P0.2 — Fix `hermes_state` imports** (108 refs)
  - `from hermes_state` → `from centurion_state`
  - `import hermes_state` → `import centurion_state`

- [ ] **P0.3 — Fix `hermes_constants` imports** (136 refs)
  - `from hermes_constants` → `from centurion_constants`
  - `import hermes_constants` → `import centurion_constants`

- [ ] **P0.4 — Fix `hermes_logging` imports** (92 refs)
  - `from hermes_logging` → `from centurion_logging`

- [ ] **P0.5 — Fix `hermes_bootstrap` imports** (27 refs)
  - `from hermes_bootstrap` → `from centurion_bootstrap`

- [ ] **P0.6 — Fix `hermes_time` imports** (37 refs)
  - `from hermes_time` → `from centurion_time`

- [ ] **P0.7 — Fix `pyproject.toml` dependencies**
  - `hermes-agent[cron]` → `centurionai-os[cron]`
  - `hermes-agent[cli]` → `centurionai-os[cli]`
  - `hermes-agent[pty]` → `centurionai-os[pty]`
  - Also check any other pip dependency references

- [ ] **P0.8 — CLI entry point script**
  - The `hermes` shebang at repo root needs to invoke `centurion` CLI, not `hermes`
  - Should we keep `hermes` as a compat symlink? Decision needed.

### 🟡 P1 — Should Fix for Consistency

These don't break runtime but create confusion.

- [ ] **P1.1 — Rename internal function/variable names**
  - `get_hermes_home()` → `get_centurion_home()` (in centurion_constants.py)
  - `load_hermes_dotenv()` → `load_centurion_dotenv()` (in centurion_cli/env_loader.py)
  - `_HERMES_VERSION` → `_CENTURION_VERSION` (in centurion_cli/__init__.py)
  - All similar function/variable renames across the codebase
  - Approach: grep for surviving `hermes` in Python source after P0, then rename by semantic group

- [ ] **P1.2 — Skills: built-in (107 files)**
  - The `hermes-agent` skill at `skills/autonomous-ai-agents/hermes-agent/` references `hermes` throughout
  - Also every other built-in skill that mentions `hermes` in its SKILL.md
  - These affect user-facing experience (e.g. "Use `hermes logs`" in skill instructions)

- [ ] **P1.3 — GitHub CI / GitHub config (14 files)**
  - Workflow names, action names, job names
  - `.github/actions/hermes-smoke-test/action.yml`
  - `.github/dependabot.yml` (package-ecosystem reference)
  - Issue/PR templates

- [ ] **P1.4 — Shell scripts (13 files)**
  - Install script (`scripts/install.sh`, `setup-hermes.sh`)
  - Docker entrypoint scripts
  - Check for any `hermes` binary references

- [ ] **P1.5 — Config files (44 yaml/toml/json)**
  - docker-compose.yml
  - cli-config.yaml.example
  - Various example config files

- [ ] **P1.6 — Plugin name: `hermes-achievements`**
  - Directory `plugins/hermes-achievements/`
  - Rename to `centurion-achievements/` or keep as heritage reference?

### 🟢 P2 — Cosmetic / Documentation

- [ ] **P2.1 — Website/docs** (588 files)
  - The Docusaurus site at `website/`
  - Bulk search-and-replace across all .md, .tsx, .json files
  - URLs will need updating
  - i18n translations (Chinese, Japanese, etc.) need updating too

- [ ] **P2.2 — Translation/locale files** (27 files)
  - `locales/*.yaml` — user-facing UI labels

- [ ] **P2.3 — README files** (21 files)
  - Root `README.md` and sub-project READMEs

- [ ] **P2.4 — Web dashboard** 
  - `web/src/` — React dashboard UI references `hermes` in components, i18n, themes

- [ ] **P2.5 — Release notes**
  - `RELEASE_v*.md` — historical. Consider a forward note at the top of each.

### 🔬 P3 — Strategic / Future-Proofing

- [ ] **P3.1 — Upstream merge strategy**
  - How to handle future upstream Hermes changes
  - Decision: cherry-pick vs rebase vs manual merge

- [ ] **P3.2 — Heritage tracking**
  - Where/how to reference the Hermes origin
  - Suggested: CONTRIBUTING.md or a HERITAGE.md file

- [ ] **P3.3 — Skills registry**
  - Skills from the Hermes registry will install files that reference `hermes_tools`
  - Need either: (a) compatibility layer in Centurion, or (b) forked skills registry

---

## Estimated Effort

| Priority | Items | Files | Type | Est. Time |
|----------|-------|-------|------|-----------|
| P0 | 8 | ~1,100 | Mechanical sed + verify | 30-60 min |
| P1 | 6 | ~130 | Semi-automated | 60-90 min |
| P2 | 5 | ~620 | Bulk replace + manual check | 2-3 hrs |
| P3 | 3 | N/A | Design decisions | Human time |

---

## Approach Recommendation

**For P0:** Use targeted `sed` per file type. Don't do a blanket `find | sed` — you'll hit strings inside strings. Better: Python script that reads each `.py` file, replaces import lines only, and writes back.

**For P1:** Semi-automated — grep for surviving `hermes` in Python source after P0, then rename by semantic group. Some will need manual review (function names may have meaning).

**For P2:** Bulk `sed` is safe here — docs and UI labels don't have import semantics.

**For P3:** Needs Adrian's input — these are design decisions, not mechanical changes.

---

## Verification After Each Phase

1. `grep -r 'from hermes_\|import hermes_' --include='*.py' | wc -l` should hit zero after P0
2. `grep -ri 'hermes' --include='*.py' | grep -v '__pycache__' | grep -v '.pyc'` should approach zero after P1
3. Try `python3 -c "from centurion_cli import *"` to test clean imports
4. Run `python3 setup.py check` or equivalent
