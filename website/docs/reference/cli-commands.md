---
sidebar_position: 1
title: "CLI Commands Reference"
description: "Authoritative reference for Centurion terminal commands and command families"
---

# CLI Commands Reference

This page covers the **terminal commands** you run from your shell.

For in-chat slash commands, see [Slash Commands Reference](./slash-commands.md).

## Global entrypoint

```bash
centurion [global-options] <command> [subcommand/options]
```

### Global options

| Option | Description |
|--------|-------------|
| `--version`, `-V` | Show version and exit. |
| `--profile <name>`, `-p <name>` | Select which Centurion profile to use for this invocation. Overrides the sticky default set by `centurion profile use`. |
| `--resume <session>`, `-r <session>` | Resume a previous session by ID or title. |
| `--continue [name]`, `-c [name]` | Resume the most recent session, or the most recent session matching a title. |
| `--worktree`, `-w` | Start in an isolated git worktree for parallel-agent workflows. |
| `--yolo` | Bypass dangerous-command approval prompts. |
| `--pass-session-id` | Include the session ID in the agent's system prompt. |
| `--ignore-user-config` | Ignore `~/.centurion/config.yaml` and fall back to built-in defaults. Credentials in `.env` are still loaded. |
| `--ignore-rules` | Skip auto-injection of `AGENTS.md`, `SOUL.md`, `.cursorrules`, memory, and preloaded skills. |
| `--tui` | Launch the [TUI](../user-guide/tui.md) instead of the classic CLI. Equivalent to `CENTURION_TUI=1`. |
| `--dev` | With `--tui`: run the TypeScript sources directly via `tsx` instead of the prebuilt bundle (for TUI contributors). |

## Top-level commands

| Command | Purpose |
|---------|---------|
| `centurion chat` | Interactive or one-shot chat with the agent. |
| `centurion model` | Interactively choose the default provider and model. |
| `centurion fallback` | Manage fallback providers tried when the primary model errors. |
| `centurion gateway` | Run or manage the messaging gateway service. |
| `centurion proxy` | Local OpenAI-compatible proxy that attaches OAuth provider credentials. See [Subscription Proxy](../user-guide/features/subscription-proxy.md). |
| `centurion lsp` | Manage Language Server Protocol integration (semantic diagnostics for write_file/patch). |
| `centurion setup` | Interactive setup wizard for all or part of the configuration. |
| `centurion whatsapp` | Configure and pair the WhatsApp bridge. |
| `centurion slack` | Slack helpers (currently: generate the app manifest with every command as a native slash). |
| `centurion auth` | Manage credentials — add, list, remove, reset, set strategy. Handles OAuth flows for Codex/Nous/Anthropic. |
| `centurion login` / `logout` | **Deprecated** — use `centurion auth` instead. |
| `centurion status` | Show agent, auth, and platform status. |
| `centurion cron` | Inspect and tick the cron scheduler. |
| `centurion kanban` | Multi-profile collaboration board (tasks, links, dispatcher). |
| `centurion webhook` | Manage dynamic webhook subscriptions for event-driven activation. |
| `centurion hooks` | Inspect, approve, or remove shell-script hooks declared in `config.yaml`. |
| `centurion doctor` | Diagnose config and dependency issues. |
| `centurion security audit` | On-demand supply-chain audit (OSV.dev) for the venv, plugin requirements, and pinned MCP servers. |
| `centurion dump` | Copy-pasteable setup summary for support/debugging. |
| `centurion debug` | Debug tools — upload logs and system info for support. |
| `centurion backup` | Back up Centurion home directory to a zip file. |
| `centurion checkpoints` | Inspect / prune / clear `~/.centurion/checkpoints/` (the shadow store used by `/rollback`). Run with no args for a status overview. |
| `centurion import` | Restore a Centurion backup from a zip file. |
| `centurion logs` | View, tail, and filter agent/gateway/error log files. |
| `centurion config` | Show, edit, migrate, and query configuration files. |
| `centurion pairing` | Approve or revoke messaging pairing codes. |
| `centurion skills` | Browse, install, publish, audit, and configure skills. |
| `centurion bundles` | Group several skills under a single `/<name>` slash command. See [Skill Bundles](../user-guide/features/skills.md#skill-bundles). |
| `centurion curator` | Background skill maintenance — status, run, pause, pin. See [Curator](../user-guide/features/curator.md). |
| `centurion memory` | Configure external memory provider. Plugin-specific subcommands (e.g. `centurion honcho`) register automatically when their provider is active. |
| `centurion acp` | Run Centurion as an ACP server for editor integration. |
| `centurion mcp` | Manage MCP server configurations and run Centurion as an MCP server. |
| `centurion plugins` | Manage Centurion AI OS plugins (install, enable, disable, remove). |
| `centurion portal` | Centurion Portal status, subscription link, and Tool Gateway routing. See [Tool Gateway](../user-guide/features/tool-gateway.md). |
| `centurion tools` | Configure enabled tools per platform. |
| `centurion computer-use` | Install or check the cua-driver backend (macOS Computer Use). |
| `centurion sessions` | Browse, export, prune, rename, and delete sessions. |
| `centurion insights` | Show token/cost/activity analytics. |
| `centurion claw` | OpenClaw migration helpers. |
| `centurion dashboard` | Launch the web dashboard for managing config, API keys, and sessions. |
| `centurion profile` | Manage profiles — multiple isolated Centurion instances. |
| `centurion completion` | Print shell completion scripts (bash/zsh/fish). |
| `centurion version` | Show version information. |
| `centurion update` | Pull latest code and reinstall dependencies (git installs), or check PyPI and `pip install --upgrade` (pip installs). `--check` previews without installing; `--backup` takes a pre-pull `CENTURION_HOME` snapshot. |
| `centurion uninstall` | Remove Centurion from the system. |

## `centurion chat`

```bash
centurion chat [options]
```

Common options:

| Option | Description |
|--------|-------------|
| `-q`, `--query "..."` | One-shot, non-interactive prompt. |
| `-m`, `--model <model>` | Override the model for this run. |
| `-t`, `--toolsets <csv>` | Enable a comma-separated set of toolsets. |
| `--provider <provider>` | Force a provider: `auto`, `openrouter`, `nous`, `openai-codex`, `copilot-acp`, `copilot`, `anthropic`, `gemini`, `google-gemini-cli`, `huggingface`, `novita`, `zai`, `kimi-coding`, `kimi-coding-cn`, `minimax`, `minimax-cn`, `minimax-oauth`, `kilocode`, `xiaomi`, `arcee`, `gmi`, `alibaba`, `alibaba-coding-plan` (alias `alibaba_coding`), `deepseek`, `nvidia`, `ollama-cloud`, `xai` (alias `grok`), `xai-oauth` (alias `grok-oauth`), `qwen-oauth`, `bedrock`, `opencode-zen`, `opencode-go`, `ai-gateway`, `azure-foundry`, `lmstudio`, `stepfun`, `tencent-tokenhub` (alias `tencent`, `tokenhub`). |
| `-s`, `--skills <name>` | Preload one or more skills for the session (can be repeated or comma-separated). |
| `-v`, `--verbose` | Verbose output. |
| `-Q`, `--quiet` | Programmatic mode: suppress banner/spinner/tool previews. |
| `--image <path>` | Attach a local image to a single query. |
| `--resume <session>` / `--continue [name]` | Resume a session directly from `chat`. |
| `--worktree` | Create an isolated git worktree for this run. |
| `--checkpoints` | Enable filesystem checkpoints before destructive file changes. |
| `--yolo` | Skip approval prompts. |
| `--pass-session-id` | Pass the session ID into the system prompt. |
| `--ignore-user-config` | Ignore `~/.centurion/config.yaml` and use built-in defaults. Credentials in `.env` are still loaded. Useful for isolated CI runs, reproducible bug reports, and third-party integrations. |
| `--ignore-rules` | Skip auto-injection of `AGENTS.md`, `SOUL.md`, `.cursorrules`, persistent memory, and preloaded skills. Combine with `--ignore-user-config` for a fully isolated run. |
| `--source <tag>` | Session source tag for filtering (default: `cli`). Use `tool` for third-party integrations that should not appear in user session lists. |
| `--max-turns <N>` | Maximum tool-calling iterations per conversation turn (default: 90, or `agent.max_turns` in config). |

Examples:

```bash
centurion
centurion chat -q "Summarize the latest PRs"
centurion chat --provider openrouter --model anthropic/claude-sonnet-4.6
centurion chat --toolsets web,terminal,skills
centurion chat --quiet -q "Return only JSON"
centurion chat --worktree -q "Review this repo and open a PR"
centurion chat --ignore-user-config --ignore-rules -q "Repro without my personal setup"
```

### `centurion -z <prompt>` — scripted one-shot

For programmatic callers (shell scripts, CI, cron, parent processes piping in a prompt), `centurion -z` is the purest one-shot entry point: **single prompt in, final response text out, nothing else on stdout or stderr.** No banner, no spinner, no tool previews, no `Session:` line — just the agent's final reply as plain text.

```bash
centurion -z "What's the capital of France?"
# → Paris.

# Parent scripts can cleanly capture the response:
answer=$(centurion -z "summarize this" < /path/to/file.txt)
```

Per-run overrides (no mutation to `~/.centurion/config.yaml`):

| Flag | Equivalent env var | Purpose |
|---|---|---|
| `-m` / `--model <model>` | `CENTURION_INFERENCE_MODEL` | Override the model for this run |
| `--provider <provider>` | _(none)_ | Override the provider for this run |

```bash
centurion -z "…" --provider openrouter --model openai/gpt-5.5
# or:
CENTURION_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 centurion -z "…"
```

Same agent, same tools, same skills — just strips every interactive / cosmetic layer. If you need tool output in the transcript too, use `centurion chat -q` instead; `-z` is explicitly for "I only want the final answer".

## `centurion model`

Interactive provider + model selector. **This is the command for adding new providers, setting up API keys, and running OAuth flows.** Run it from your terminal — not from inside an active Centurion chat session.

```bash
centurion model
```

Use this when you want to:
- **add a new provider** (OpenRouter, Anthropic, Copilot, DeepSeek, custom, etc.)
- log into OAuth-backed providers (Anthropic, Copilot, Codex, Centurion Portal)
- enter or update API keys
- pick from provider-specific model lists
- configure a custom/self-hosted endpoint
- save the new default into config

:::warning centurion model vs /model — know the difference
**`centurion model`** (run from your terminal, outside any Centurion session) is the **full provider setup wizard**. It can add new providers, run OAuth flows, prompt for API keys, and configure endpoints.

**`/model`** (typed inside an active Centurion chat session) can only **switch between providers and models you've already set up**. It cannot add new providers, run OAuth, or prompt for API keys.

**If you need to add a new provider:** Exit your Centurion session first (`Ctrl+C` or `/quit`), then run `centurion model` from your terminal prompt.
:::

### `/model` slash command (mid-session)

Switch between already-configured models without leaving a session:

```
/model                              # Show current model and available options
/model claude-sonnet-4              # Switch model (auto-detects provider)
/model zai:glm-5                    # Switch provider and model
/model custom:qwen-2.5              # Use model on your custom endpoint
/model custom                       # Auto-detect model from custom endpoint
/model custom:local:qwen-2.5        # Use a named custom provider
/model openrouter:anthropic/claude-sonnet-4  # Switch back to cloud
```

By default, `/model` changes apply **to the current session only**. Add `--global` to persist the change to `config.yaml`:

```
/model claude-sonnet-4 --global     # Switch and save as new default
```

:::info What if I only see OpenRouter models?
If you've only configured OpenRouter, `/model` will only show OpenRouter models. To add another provider (Anthropic, DeepSeek, Copilot, etc.), exit your session and run `centurion model` from the terminal.
:::

Provider and base URL changes are persisted to `config.yaml` automatically. When switching away from a custom endpoint, the stale base URL is cleared to prevent it leaking into other providers.

## `centurion gateway`

```bash
centurion gateway <subcommand>
```

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `run` | Run the gateway in the foreground. Recommended for WSL, Docker, and Termux. |
| `start` | Start the installed systemd/launchd background service. |
| `stop` | Stop the service (or foreground process). |
| `restart` | Restart the service. |
| `status` | Show service status. |
| `list` | List **all profiles** and whether each profile's gateway is currently running (with PID where available). Handy when you run multiple profiles side-by-side and want a single overview. |
| `install` | Install as a systemd (Linux) or launchd (macOS) background service. |
| `uninstall` | Remove the installed service. |
| `setup` | Interactive messaging-platform setup. |

Options:

| Option | Description |
|--------|-------------|
| `--all` | On `start` / `restart` / `stop`: act on **every profile's** gateway, not just the active `CENTURION_HOME`. Useful if you run multiple profiles side-by-side and want to restart them all after `centurion update`. |

:::tip WSL users
Use `centurion gateway run` instead of `centurion gateway start` — WSL's systemd support is unreliable. Wrap it in tmux for persistence: `tmux new -s centurion 'centurion gateway run'`. See [WSL FAQ](/reference/faq#wsl-gateway-keeps-disconnecting-or-centurion-gateway-start-fails) for details.
:::

## `centurion lsp`

```bash
centurion lsp <subcommand>
```

Manage the Language Server Protocol integration. LSP runs real
language servers (pyright, gopls, rust-analyzer, …) in the
background and feeds their diagnostics into the post-write check
used by `write_file` and `patch`. Gated on git workspace detection
— LSP only runs when the cwd or edited file is inside a git
worktree.

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `status` | Show service state, configured servers, install status. |
| `list` | Print the registry of supported servers. Pass `--installed-only` to skip missing ones. |
| `install <id>` | Eagerly install one server's binary. |
| `install-all` | Install every server with a known auto-install recipe. |
| `restart` | Tear down running clients so the next edit re-spawns. |
| `which <id>` | Print the resolved binary path for one server. |

See [LSP — Semantic Diagnostics](/user-guide/features/lsp) for
the full guide, supported languages, and configuration knobs.

## `centurion setup`

```bash
centurion setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure] [--portal]
```

**First run:** launches the first-time wizard.

**Returning user (already configured):** drops straight into the full reconfigure wizard — every prompt shows your current value as its default, press Enter to keep or type a new value. No menu.

Jump into one section instead of the full wizard:

| Section | Description |
|---------|-------------|
| `model` | Provider and model setup. |
| `terminal` | Terminal backend and sandbox setup. |
| `gateway` | Messaging platform setup. |
| `tools` | Enable/disable tools per platform. |
| `agent` | Agent behavior settings. |

Options:

| Option | Description |
|--------|-------------|
| `--quick` | On returning-user runs: only prompt for items that are missing or unset. Skip items you already have configured. |
| `--non-interactive` | Use defaults / environment values without prompts. |
| `--reset` | Reset configuration to defaults before setup. |
| `--reconfigure` | Backwards-compat alias — bare `centurion setup` on an existing install now does this by default. |
| `--portal` | One-shot Centurion Portal setup: log in via OAuth, set Nous as the inference provider, and opt into the [Tool Gateway](../user-guide/features/tool-gateway.md). Skips the rest of the wizard. |

## `centurion portal`

```bash
centurion portal [status|open|tools]
```

Inspect Centurion Portal auth, Tool Gateway routing, and reach the subscription page. Subcommand-less invocation runs `status`.

| Subcommand | Description |
|------------|-------------|
| `status` (default) | Portal auth state + per-tool Tool Gateway routing summary. Also shown when no subcommand is given. |
| `open` | Open `portal.personal-centurion.com/manage-subscription` in your default browser. |
| `tools` | List every Tool Gateway partner (Firecrawl, FAL, OpenAI TTS, Browser Use, Modal) and which are routed via Nous. |

For configuration of the gateway itself, see [Tool Gateway](../user-guide/features/tool-gateway.md). For the one-shot setup path, see `centurion setup --portal` above.

## `centurion whatsapp`

```bash
centurion whatsapp
```

Runs the WhatsApp pairing/setup flow, including mode selection and QR-code pairing.

## `centurion slack`

```bash
centurion slack manifest              # print manifest to stdout
centurion slack manifest --write      # write to ~/.centurion/slack-manifest.json
centurion slack manifest --slashes-only  # just the features.slash_commands array
```

Generates a Slack app manifest that registers every gateway command in
`COMMAND_REGISTRY` (`/btw`, `/stop`, `/model`, …) as a first-class
Slack slash command — matching Discord and Telegram parity. Paste the
output into your Slack app config at
[https://api.slack.com/apps](https://api.slack.com/apps) → your app →
**Features → App Manifest → Edit**, then **Save**. Slack prompts for
reinstall if scopes or slash commands changed.

| Flag | Default | Purpose |
|------|---------|---------|
| `--write [PATH]` | stdout | Write to a file instead of stdout. Bare `--write` writes `$CENTURION_HOME/slack-manifest.json`. |
| `--name NAME` | `Centurion` | Bot display name in Slack. |
| `--description DESC` | default blurb | Bot description shown in the Slack app directory. |
| `--slashes-only` | off | Emit only `features.slash_commands` for merging into a manually-maintained manifest. |

Run `centurion slack manifest --write` again after `centurion update` to pick
up any new commands.


## `centurion login` / `centurion logout` *(Deprecated)*

:::caution
`centurion login` has been removed. Use `centurion auth` to manage OAuth credentials, `centurion model` to select a provider, or `centurion setup` for full interactive setup.
:::

## `centurion auth`

Manage credential pools for same-provider key rotation. See [Credential Pools](/user-guide/features/credential-pools) for full documentation.

```bash
centurion auth                                              # Interactive wizard
centurion auth list                                         # Show all pools
centurion auth list openrouter                              # Show specific provider
centurion auth add openrouter --api-key sk-or-v1-xxx        # Add API key
centurion auth add anthropic --type oauth                   # Add OAuth credential
centurion auth remove openrouter 2                          # Remove by index
centurion auth reset openrouter                             # Clear cooldowns
centurion auth status anthropic                             # Show auth status for a provider
centurion auth logout anthropic                             # Log out and clear stored auth state
centurion auth spotify                                      # Authenticate Centurion with Spotify via PKCE
```

Subcommands: `add`, `list`, `remove`, `reset`, `status`, `logout`, `spotify`. When called with no subcommand, launches the interactive management wizard.

## `centurion status`

```bash
centurion status [--all] [--deep]
```

| Option | Description |
|--------|-------------|
| `--all` | Show all details in a shareable redacted format. |
| `--deep` | Run deeper checks that may take longer. |

## `centurion cron`

```bash
centurion cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| Subcommand | Description |
|------------|-------------|
| `list` | Show scheduled jobs. |
| `create` / `add` | Create a scheduled job from a prompt, optionally attaching one or more skills via repeated `--skill`. |
| `edit` | Update a job's schedule, prompt, name, delivery, repeat count, or attached skills. Supports `--clear-skills`, `--add-skill`, and `--remove-skill`. |
| `pause` | Pause a job without deleting it. |
| `resume` | Resume a paused job and compute its next future run. |
| `run` | Trigger a job on the next scheduler tick. |
| `remove` | Delete a scheduled job. |
| `status` | Check whether the cron scheduler is running. |
| `tick` | Run due jobs once and exit. |

## `centurion kanban`

```bash
centurion kanban [--board <slug>] <action> [options]
```

Multi-profile, multi-project collaboration board. Each install can host many boards (one per project, repo, or domain); each board is a standalone queue with its own SQLite DB and dispatcher scope. New installs start with one board called `default`, whose DB is `~/.centurion/kanban.db` for back-compat; additional boards live at `~/.centurion/kanban/boards/<slug>/kanban.db`. The gateway-embedded dispatcher sweeps every board per tick.

**Global flags (apply to every action below):**

| Flag | Purpose |
|------|---------|
| `--board <slug>` | Operate on a specific board. Defaults to the current board (set via `centurion kanban boards switch`, the `CENTURION_KANBAN_BOARD` env var, or `default`). |

**This is the human / scripting surface.** Agent workers spawned by the dispatcher drive the board through a dedicated `kanban_*` [toolset](/user-guide/features/kanban#how-workers-interact-with-the-board) (`kanban_show`, `kanban_complete`, `kanban_block`, `kanban_create`, `kanban_link`, `kanban_comment`, `kanban_heartbeat`; orchestrator profiles also get `kanban_list` and `kanban_unblock`) instead of shelling to `centurion kanban`. Workers have `CENTURION_KANBAN_BOARD` pinned in their env so they physically cannot see other boards.

| Action | Purpose |
|--------|---------|
| `init` | Create `kanban.db` if missing. Idempotent. |
| `boards list` / `boards ls` | List all boards with task counts. `--json`, `--all` (include archived). |
| `boards create <slug>` | Create a new board. Flags: `--name`, `--description`, `--icon`, `--color`, `--switch` (make active). Slug is kebab-case, auto-downcased. |
| `boards switch <slug>` / `boards use` | Persist `<slug>` as the active board (writes `~/.centurion/kanban/current`). |
| `boards show` / `boards current` | Print the currently-active board's name, DB path, and task counts. |
| `boards rename <slug> "<name>"` | Change a board's display name. Slug is immutable. |
| `boards rm <slug>` | Archive (default) or hard-delete a board. `--delete` skips the archive step. Archived boards move to `boards/_archived/<slug>-<ts>/`. Refused for `default`. |
| `create "<title>"` | Create a new task on the active board. Flags: `--body`, `--assignee`, `--parent` (repeatable), `--workspace scratch\|worktree\|dir:<path>`, `--tenant`, `--priority`, `--triage`, `--idempotency-key`, `--max-runtime`, `--max-retries`, `--skill` (repeatable). |
| `list` / `ls` | List tasks on the active board. Filter with `--mine`, `--assignee`, `--status`, `--tenant`, `--archived`, `--json`. |
| `show <id>` | Show a task with comments and events. `--json` for machine output. |
| `assign <id> <profile>` | Assign or reassign. Use `none` to unassign. Refused while task is running. |
| `link <parent> <child>` | Add a dependency. Cycle-detected. Both tasks must be on the same board. |
| `unlink <parent> <child>` | Remove a dependency. |
| `claim <id>` | Atomically claim a ready task. Prints resolved workspace path. |
| `comment <id> "<text>"` | Append a comment. The next worker that claims the task reads it as part of its `kanban_show()` response. |
| `complete <id>` | Mark task done. Flags: `--result`, `--summary`, `--metadata`. |
| `block <id> "<reason>"` | Mark task blocked for human input. Also appends the reason as a comment. |
| `schedule <id> "<reason>"` | Park time-delay/follow-up work in `scheduled` so it is not shown as a human blocker. |
| `unblock <id>` | Return a blocked or scheduled task to ready (or `todo` if dependencies are still open). |
| `archive <id>` | Hide from default list. `gc` will remove scratch workspaces. |
| `tail <id>` | Follow a task's event stream. |
| `dispatch` | One dispatcher pass on the active board. Flags: `--dry-run`, `--max N`, `--failure-limit N`, `--json`. |
| `context <id>` | Print the full context a worker would see (title + body + parent results + comments). |
| `specify <id>` / `specify --all` | Flesh out a triage-column task into a concrete spec (title + body with goal, approach, acceptance criteria) via the auxiliary LLM, then promote it to `todo`. Flags: `--tenant` (scope `--all` to one tenant), `--author`, `--json`. Configure the model under `auxiliary.triage_specifier` in `config.yaml`. |
| `decompose <id>` / `decompose --all` | Fan a triage-column task out into a graph of child tasks routed to specialist profiles by description (the orchestrator-driven path). Falls back to specify-style single-task promotion when the LLM decides the task doesn't benefit from fan-out. Same flags as `specify`. Configure the model under `auxiliary.kanban_decomposer` in `config.yaml`. Also runs automatically every dispatcher tick when `kanban.auto_decompose: true` (the default). See [Auto vs Manual orchestration](/user-guide/features/kanban#auto-vs-manual-orchestration). |
| `gc` | Remove scratch workspaces for archived tasks. |

Examples:

```bash
# Create a second board and put a task on it without switching away.
centurion kanban boards create atm10-server --name "ATM10 Server" --icon 🎮
centurion kanban --board atm10-server create "Restart server" --assignee ops

# Switch the active board for subsequent calls.
centurion kanban boards switch atm10-server
centurion kanban list                  # shows atm10-server tasks

# Archive a board (recoverable) or hard-delete it.
centurion kanban boards rm atm10-server
centurion kanban boards rm atm10-server --delete
```

Board resolution order (highest precedence first): `--board <slug>` flag → `CENTURION_KANBAN_BOARD` env var → `~/.centurion/kanban/current` file → `default`.

All actions are also available as a slash command in the gateway (`/kanban …`), with the same argument surface — including `boards` subcommands and the `--board` flag.

For the full design — comparison with Cline Kanban / Paperclip / NanoClaw / Gemini Enterprise, eight collaboration patterns, four user stories, concurrency correctness proof — see `docs/centurion-kanban-v1-spec.pdf` in the repository or the [Kanban user guide](/user-guide/features/kanban).

## `centurion webhook`

```bash
centurion webhook <subscribe|list|remove|test>
```

Manage dynamic webhook subscriptions for event-driven agent activation. Requires the webhook platform to be enabled in config — if not configured, prints setup instructions.

| Subcommand | Description |
|------------|-------------|
| `subscribe` / `add` | Create a webhook route. Returns the URL and HMAC secret to configure on your service. |
| `list` / `ls` | Show all agent-created subscriptions. |
| `remove` / `rm` | Delete a dynamic subscription. Static routes from config.yaml are not affected. |
| `test` | Send a test POST to verify a subscription is working. |

### `centurion webhook subscribe`

```bash
centurion webhook subscribe <name> [options]
```

| Option | Description |
|--------|-------------|
| `--prompt` | Prompt template with `{dot.notation}` payload references. |
| `--events` | Comma-separated event types to accept (e.g. `issues,pull_request`). Empty = all. |
| `--description` | Human-readable description. |
| `--skills` | Comma-separated skill names to load for the agent run. |
| `--deliver` | Delivery target: `log` (default), `telegram`, `discord`, `slack`, `github_comment`. |
| `--deliver-chat-id` | Target chat/channel ID for cross-platform delivery. |
| `--secret` | Custom HMAC secret. Auto-generated if omitted. |
| `--deliver-only` | Skip the agent — deliver the rendered `--prompt` as the literal message. Zero LLM cost, sub-second delivery. Requires `--deliver` to be a real target (not `log`). |

Subscriptions persist to `~/.centurion/webhook_subscriptions.json` and are hot-reloaded by the webhook adapter without a gateway restart.

## `centurion doctor`

```bash
centurion doctor [--fix]
```

| Option | Description |
|--------|-------------|
| `--fix` | Attempt automatic repairs where possible. |

## `centurion dump`

```bash
centurion dump [--show-keys]
```

Outputs a compact, plain-text summary of your entire Centurion setup. Designed to be copy-pasted into Discord, GitHub issues, or Telegram when asking for support — no ANSI colors, no special formatting, just data.

| Option | Description |
|--------|-------------|
| `--show-keys` | Show redacted API key prefixes (first and last 4 characters) instead of just `set`/`not set`. |

### What it includes

| Section | Details |
|---------|---------|
| **Header** | Centurion version, release date, git commit hash |
| **Environment** | OS, Python version, OpenAI SDK version |
| **Identity** | Active profile name, CENTURION_HOME path |
| **Model** | Configured default model and provider |
| **Terminal** | Backend type (local, docker, ssh, etc.) |
| **API keys** | Presence check for all 22 provider/tool API keys |
| **Features** | Enabled toolsets, MCP server count, memory provider |
| **Services** | Gateway status, configured messaging platforms |
| **Workload** | Cron job counts, installed skill count |
| **Config overrides** | Any config values that differ from defaults |

### Example output

```
--- centurion dump ---
version:          0.8.0 (2026.4.8) [af4abd2f]
os:               Linux 6.14.0-37-generic x86_64
python:           3.11.14
openai_sdk:       2.24.0
profile:          default
centurion_home:      ~/.centurion
model:            anthropic/claude-opus-4.6
provider:         openrouter
terminal:         local

api_keys:
  openrouter           set
  openai               not set
  anthropic            set
  nous                 not set
  firecrawl            set
  ...

features:
  toolsets:           all
  mcp_servers:        0
  memory_provider:    built-in
  gateway:            running (systemd)
  platforms:          telegram, discord
  cron_jobs:          3 active / 5 total
  skills:             42

config_overrides:
  agent.max_turns: 250
  compression.threshold: 0.85
  display.streaming: True
--- end dump ---
```

### When to use

- Reporting a bug on GitHub — paste the dump into your issue
- Asking for help in Discord — share it in a code block
- Comparing your setup to someone else's
- Quick sanity check when something isn't working

:::tip
`centurion dump` is specifically designed for sharing. For interactive diagnostics, use `centurion doctor`. For a visual overview, use `centurion status`.
:::

## `centurion debug`

```bash
centurion debug share [options]
```

Upload a debug report (system info + recent logs) to a paste service and get a shareable URL. Useful for quick support requests — includes everything a helper needs to diagnose your issue.

| Option | Description |
|--------|-------------|
| `--lines <N>` | Number of log lines to include per log file (default: 200). |
| `--expire <days>` | Paste expiry in days (default: 7). |
| `--local` | Print the report locally instead of uploading. |

The report includes system info (OS, Python version, Centurion version), recent agent and gateway logs (512 KB limit per file), and redacted API key status. Keys are always redacted — no secrets are uploaded.

Paste services tried in order: paste.rs, dpaste.com.

### Examples

```bash
centurion debug share              # Upload debug report, print URL
centurion debug share --lines 500  # Include more log lines
centurion debug share --expire 30  # Keep paste for 30 days
centurion debug share --local      # Print report to terminal (no upload)
```

## `centurion backup`

```bash
centurion backup [options]
```

Create a zip archive of your Centurion configuration, skills, sessions, and data. The backup excludes the centurion-ai-os codebase itself.

| Option | Description |
|--------|-------------|
| `-o`, `--output <path>` | Output path for the zip file (default: `~/centurion-backup-<timestamp>.zip`). |
| `-q`, `--quick` | Quick snapshot: only critical state files (config.yaml, state.db, .env, auth, cron jobs). Much faster than a full backup. |
| `-l`, `--label <name>` | Label for the snapshot (only used with `--quick`). |

The backup uses SQLite's `backup()` API for safe copying, so it works correctly even when Centurion is running (WAL-mode safe).

**What's excluded from the zip:**

- `*.db-wal`, `*.db-shm`, `*.db-journal` — SQLite's WAL / shared-memory / journal sidecars. The `*.db` file already got a consistent snapshot via `sqlite3.backup()`; shipping the live sidecars alongside it would let a restore see a half-committed state.
- `checkpoints/` — per-session trajectory caches. Hash-keyed and regenerated per session; wouldn't port cleanly to another install anyway.
- The `centurion-ai-os` code itself (this is a user-data backup, not a repo snapshot).

### Examples

```bash
centurion backup                           # Full backup to ~/centurion-backup-*.zip
centurion backup -o /tmp/centurion.zip        # Full backup to specific path
centurion backup --quick                   # Quick state-only snapshot
centurion backup --quick --label "pre-upgrade"  # Quick snapshot with label
```

## `centurion checkpoints`

```bash
centurion checkpoints [COMMAND]
```

Inspect and manage the shadow git store at `~/.centurion/checkpoints/` — the storage layer behind the in-session `/rollback` command. Safe to run any time; does not require the agent to be running.

| Subcommand | Description |
|------------|-------------|
| `status` (default) | Show total size, project count, and per-project breakdown. Bare `centurion checkpoints` is equivalent. |
| `list` | Alias for `status`. |
| `prune` | Force a cleanup sweep — delete orphan and stale projects, GC the store, enforce the size cap. Ignores the 24h idempotency marker. |
| `clear` | Delete the entire checkpoint base. Irreversible; asks for confirmation unless `-f`. |
| `clear-legacy` | Delete only the `legacy-<timestamp>/` archives produced by the v1→v2 migration. |

### Options

| Option | Subcommand | Description |
|--------|------------|-------------|
| `--limit N` | `status`, `list` | Max projects to list (default 20). |
| `--retention-days N` | `prune` | Drop projects whose `last_touch` is older than N days (default 7). |
| `--max-size-mb N` | `prune` | After the orphan/stale pass, drop the oldest commit per project until total store size ≤ N MB (default 500). |
| `--keep-orphans` | `prune` | Skip deleting projects whose working directory no longer exists. |
| `-f`, `--force` | `clear`, `clear-legacy` | Skip the confirmation prompt. |

### Examples

```bash
centurion checkpoints                                  # status overview
centurion checkpoints prune --retention-days 3         # aggressive cleanup
centurion checkpoints prune --max-size-mb 200          # tighten size cap once
centurion checkpoints clear-legacy -f                  # drop v1 archive dirs
centurion checkpoints clear -f                         # wipe everything
```

See [Checkpoints and `/rollback`](../user-guide/checkpoints-and-rollback.md) for the full architecture and the in-session commands.

## `centurion import`

```bash
centurion import <zipfile> [options]
```

Restore a previously created Centurion backup into your Centurion home directory. All files in the archive overwrite existing files in your Centurion home; `--force` only skips the confirmation prompt that fires when the target already has a Centurion installation.

| Option | Description |
|--------|-------------|
| `-f`, `--force` | Skip the existing-installation confirmation prompt. |

:::warning
Stop the gateway before importing to avoid conflicts with running processes.
:::

### Examples
```bash
centurion import ~/centurion-backup-20260423.zip           # Prompts before overwriting existing config
centurion import ~/centurion-backup-20260423.zip --force   # Overwrite without prompting
```

## `centurion logs`

```bash
centurion logs [log_name] [options]
```

View, tail, and filter Centurion log files. All logs are stored in `~/.centurion/logs/` (or `<profile>/logs/` for non-default profiles).

### Log files

| Name | File | What it captures |
|------|------|-----------------|
| `agent` (default) | `agent.log` | All agent activity — API calls, tool dispatch, session lifecycle (INFO and above) |
| `errors` | `errors.log` | Warnings and errors only — a filtered subset of agent.log |
| `gateway` | `gateway.log` | Messaging gateway activity — platform connections, message dispatch, webhook events |

### Options

| Option | Description |
|--------|-------------|
| `log_name` | Which log to view: `agent` (default), `errors`, `gateway`, or `list` to show available files with sizes. |
| `-n`, `--lines <N>` | Number of lines to show (default: 50). |
| `-f`, `--follow` | Follow the log in real time, like `tail -f`. Press Ctrl+C to stop. |
| `--level <LEVEL>` | Minimum log level to show: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `--session <ID>` | Filter lines containing a session ID substring. |
| `--since <TIME>` | Show lines from a relative time ago: `30m`, `1h`, `2d`, etc. Supports `s` (seconds), `m` (minutes), `h` (hours), `d` (days). |
| `--component <NAME>` | Filter by component: `gateway`, `agent`, `tools`, `cli`, `cron`. |

### Examples

```bash
# View the last 50 lines of agent.log (default)
centurion logs

# Follow agent.log in real time
centurion logs -f

# View the last 100 lines of gateway.log
centurion logs gateway -n 100

# Show only warnings and errors from the last hour
centurion logs --level WARNING --since 1h

# Filter by a specific session
centurion logs --session abc123

# Follow errors.log, starting from 30 minutes ago
centurion logs errors --since 30m -f

# List all log files with their sizes
centurion logs list
```

### Filtering

Filters can be combined. When multiple filters are active, a log line must pass **all** of them to be shown:

```bash
# WARNING+ lines from the last 2 hours containing session "tg-12345"
centurion logs --level WARNING --since 2h --session tg-12345
```

Lines without a parseable timestamp are included when `--since` is active (they may be continuation lines from a multi-line log entry). Lines without a detectable level are included when `--level` is active.

### Log rotation

Centurion uses Python's `RotatingFileHandler`. Old logs are rotated automatically — look for `agent.log.1`, `agent.log.2`, etc. The `centurion logs list` subcommand shows all log files including rotated ones.

## `centurion config`

```bash
centurion config <subcommand>
```

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `show` | Show current config values. |
| `edit` | Open `config.yaml` in your editor. |
| `set <key> <value>` | Set a config value. |
| `path` | Print the config file path. |
| `env-path` | Print the `.env` file path. |
| `check` | Check for missing or stale config. |
| `migrate` | Add newly introduced options interactively. |

## `centurion pairing`

```bash
centurion pairing <list|approve|revoke|clear-pending>
```

| Subcommand | Description |
|------------|-------------|
| `list` | Show pending and approved users. |
| `approve <platform> <code>` | Approve a pairing code. |
| `revoke <platform> <user-id>` | Revoke a user's access. |
| `clear-pending` | Clear pending pairing codes. |

## `centurion skills`

```bash
centurion skills <subcommand>
```

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `browse` | Paginated browser for skill registries. |
| `search` | Search skill registries. |
| `install` | Install a skill. |
| `inspect` | Preview a skill without installing it. |
| `list` | List installed skills. |
| `check` | Check installed hub skills for upstream updates. |
| `update` | Reinstall hub skills with upstream changes when available. |
| `audit` | Re-scan installed hub skills. |
| `uninstall` | Remove a hub-installed skill. |
| `reset` | Un-stick a bundled skill flagged as `user_modified` by clearing its manifest entry. With `--restore`, also replaces the user copy with the bundled version. |
| `publish` | Publish a skill to a registry. |
| `snapshot` | Export/import skill configurations. |
| `tap` | Manage custom skill sources. |
| `config` | Interactive enable/disable configuration for skills by platform. |

Common examples:

```bash
centurion skills browse
centurion skills browse --source official
centurion skills search react --source skills-sh
centurion skills search https://mintlify.com/docs --source well-known
centurion skills inspect official/security/1password
centurion skills inspect skills-sh/vercel-labs/json-render/json-render-react
centurion skills install official/migration/openclaw-migration
centurion skills install skills-sh/anthropics/skills/pdf --force
centurion skills install https://sharethis.chat/SKILL.md                     # Direct URL (single-file SKILL.md)
centurion skills install https://example.com/SKILL.md --name my-skill        # Override name when frontmatter has none
centurion skills check
centurion skills update
centurion skills config
centurion skills reset google-workspace
centurion skills reset google-workspace --restore --yes
```

Notes:
- `--force` can override non-dangerous policy blocks for third-party/community skills.
- `--force` does not override a `dangerous` scan verdict.
- `--source skills-sh` searches the public `skills.sh` directory.
- `--source well-known` lets you point Centurion at a site exposing `/.well-known/skills/index.json`.
- `--source browse-sh` searches [browse.sh](https://browse.sh)'s catalog of 200+ site-specific browser-automation skills. Identifiers look like `browse-sh/airbnb.com/search-listings-ddgioa`.
- Passing an `http(s)://…/*.md` URL installs a single-file SKILL.md directly. When frontmatter has no `name:` and the URL slug isn't a valid identifier, an interactive terminal prompts for a name; non-interactive surfaces (`/skills install` inside the TUI, gateway platforms) require `--name <x>` instead.

## `centurion bundles`

```bash
centurion bundles <subcommand>
```

Skill bundles group several skills under one `/<bundle-name>` slash command. Invoking the bundle loads every referenced skill into a single combined user message. Storage: `~/.centurion/skill-bundles/<slug>.yaml`. See [Skill Bundles](../user-guide/features/skills.md#skill-bundles) for the YAML schema and behavior.

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `list` | List installed bundles (default when no subcommand given) |
| `show <name>` | Show one bundle's name, description, skills, and file path |
| `create <name>` | Create a new bundle. Pass `--skill <id>` (repeat) or omit for interactive entry. `--description`, `--instruction`, `--force` available. |
| `delete <name>` | Remove a bundle file |
| `reload` | Re-scan `~/.centurion/skill-bundles/` and report added/removed bundles |

Examples:

```bash
centurion bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work"

centurion bundles list
centurion bundles show backend-dev
centurion bundles delete backend-dev
```

In a chat session, `/bundles` lists installed bundles and `/<bundle-name>` loads one.

## `centurion curator`

```bash
centurion curator <subcommand>
```

The curator is an auxiliary-model background task that periodically reviews agent-created skills, prunes stale ones, consolidates overlaps, and archives obsolete skills. Bundled and hub-installed skills are never touched. Archives are recoverable; auto-deletion never happens.

| Subcommand | Description |
|------------|-------------|
| `status` | Show curator status and skill stats |
| `run` | Trigger a curator review now (blocks until the LLM pass finishes) |
| `run --background` | Start the LLM pass in a background thread and return immediately |
| `run --dry-run` | Preview only — produce the review report with no mutations |
| `backup` | Take a manual tar.gz snapshot of `~/.centurion/skills/` (curator also snapshots automatically before every real run) |
| `rollback` | Restore `~/.centurion/skills/` from a snapshot (defaults to newest) |
| `rollback --list` | List available snapshots |
| `rollback --id <ts>` | Restore a specific snapshot by id |
| `rollback -y` | Skip the confirmation prompt |
| `pause` | Pause the curator until resumed |
| `resume` | Resume a paused curator |
| `pin <skill>` | Pin a skill so the curator never auto-transitions it |
| `unpin <skill>` | Unpin a skill |
| `restore <skill>` | Restore an archived skill |
| `archive <skill>` | Archive a skill manually |
| `prune` | Manually prune skills the curator would normally clean up |
| `list-archived` | List archived skills (recoverable via `restore`) |

On a fresh install the first scheduled pass is deferred by one full `interval_hours` (7 days by default) — the gateway will not curate immediately on the first tick after `centurion update`. Use `centurion curator run --dry-run` to preview before that happens.

See [Curator](../user-guide/features/curator.md) for behavior and config.

## `centurion fallback`

```bash
centurion fallback <subcommand>
```

Manage the fallback provider chain. Fallback providers are tried in order when the primary model fails with rate-limit, overload, or connection errors.

| Subcommand | Description |
|------------|-------------|
| `list` (alias: `ls`) | Show the current fallback chain (default when no subcommand) |
| `add` | Pick a provider + model (same picker as `centurion model`) and append to the chain |
| `remove` (alias: `rm`) | Pick an entry to delete from the chain |
| `clear` | Remove all fallback entries |

See [Fallback Providers](../user-guide/features/fallback-providers.md).

## `centurion hooks`

```bash
centurion hooks <subcommand>
```

Inspect shell-script hooks declared in `~/.centurion/config.yaml`, test them against synthetic payloads, and manage the first-use consent allowlist at `~/.centurion/shell-hooks-allowlist.json`.

| Subcommand | Description |
|------------|-------------|
| `list` (alias: `ls`) | List configured hooks with matcher, timeout, and consent status |
| `test <event>` | Fire every hook matching `<event>` against a synthetic payload |
| `revoke` (aliases: `remove`, `rm`) | Remove a command's allowlist entries (takes effect on next restart) |
| `doctor` | Check each configured hook: exec bit, allowlist, mtime drift, JSON validity, and synthetic run timing |

See [Hooks](../user-guide/features/hooks.md) for event signatures and payload shapes.

## `centurion memory`

```bash
centurion memory <subcommand>
```

Set up and manage external memory provider plugins. Available providers: honcho, openviking, mem0, hindsight, holographic, retaindb, byterover, supermemory. Only one external provider can be active at a time. Built-in memory (MEMORY.md/USER.md) is always active.

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `setup` | Interactive provider selection and configuration. |
| `status` | Show current memory provider config. |
| `off` | Disable external provider (built-in only). |

:::info Provider-specific subcommands
When an external memory provider is active, it may register its own top-level `centurion <provider>` command for provider-specific management (e.g. `centurion honcho` when Honcho is active). Inactive providers do not expose their subcommands. Run `centurion --help` to see what's currently wired in.
:::

## `centurion acp`

```bash
centurion acp
```

Starts Centurion as an ACP (Agent Client Protocol) stdio server for editor integration.

Related entrypoints:

```bash
centurion-acp
python -m acp_adapter
```

Install support first:

```bash
pip install -e '.[acp]'
```

See [ACP Editor Integration](../user-guide/features/acp.md) and [ACP Internals](../developer-guide/acp-internals.md).

## `centurion mcp`

```bash
centurion mcp <subcommand>
```

Manage MCP (Model Context Protocol) server configurations and run Centurion as an MCP server.

| Subcommand | Description |
|------------|-------------|
| `serve [-v\|--verbose]` | Run Centurion as an MCP server — expose conversations to other agents. |
| `add <name> [--url URL] [--command CMD] [--args ...] [--auth oauth\|header]` | Add an MCP server with automatic tool discovery. |
| `remove <name>` (alias: `rm`) | Remove an MCP server from config. |
| `list` (alias: `ls`) | List configured MCP servers. |
| `test <name>` | Test connection to an MCP server. |
| `configure <name>` (alias: `config`) | Toggle tool selection for a server. |
| `login <name>` | Force re-authentication for an OAuth-based MCP server. |

See [MCP Config Reference](./mcp-config-reference.md), [Use MCP with Centurion](../guides/use-mcp-with-centurion.md), and [MCP Server Mode](../user-guide/features/mcp.md#running-centurion-as-an-mcp-server).

## `centurion plugins`

```bash
centurion plugins [subcommand]
```

Unified plugin management — general plugins, memory providers, and context engines in one place. Running `centurion plugins` with no subcommand opens a composite interactive screen with two sections:

- **General Plugins** — multi-select checkboxes to enable/disable installed plugins
- **Provider Plugins** — single-select configuration for Memory Provider and Context Engine. Press ENTER on a category to open a radio picker.

| Subcommand | Description |
|------------|-------------|
| *(none)* | Composite interactive UI — general plugin toggles + provider plugin configuration. |
| `install <identifier> [--force]` | Install a plugin from a Git URL or `owner/repo`. |
| `update <name>` | Pull latest changes for an installed plugin. |
| `remove <name>` (aliases: `rm`, `uninstall`) | Remove an installed plugin. |
| `enable <name>` | Enable a disabled plugin. |
| `disable <name>` | Disable a plugin without removing it. |
| `list` (alias: `ls`) | List installed plugins with enabled/disabled status. |

Provider plugin selections are saved to `config.yaml`:
- `memory.provider` — active memory provider (empty = built-in only)
- `context.engine` — active context engine (`"compressor"` = built-in default)

General plugin disabled list is stored in `config.yaml` under `plugins.disabled`.

See [Plugins](../user-guide/features/plugins.md) and [Build a Centurion Plugin](../guides/build-a-centurion-plugin.md).

## `centurion tools`

```bash
centurion tools [--summary]
```

| Option | Description |
|--------|-------------|
| `--summary` | Print the current enabled-tools summary and exit. |

Without `--summary`, this launches the interactive per-platform tool configuration UI.

## `centurion computer-use`

```bash
centurion computer-use <subcommand>
```

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `install` | Run the upstream cua-driver installer (macOS only). |
| `install --upgrade` | Re-run the installer even if cua-driver is already on PATH. The upstream script always pulls the latest release, so this performs an in-place upgrade. |
| `status` | Print whether `cua-driver` is on `$PATH` and which version is installed. |

`centurion computer-use install` is the stable entry point for installing the
[cua-driver](https://github.com/trycua/cua) binary used by the
`computer_use` toolset. It runs the same upstream installer that
`centurion tools` invokes when you first enable Computer Use, so it's safe
to use for re-running the install if the toolset toggle didn't trigger
it (for example, on returning-user setups).

`centurion update` automatically re-runs the upstream installer at the end
of the update if cua-driver is on PATH, so most users will not need to
call `--upgrade` manually. Use it when upstream ships a fix you want
right now without waiting for the next Centurion update.

## `centurion sessions`

```bash
centurion sessions <subcommand>
```

Subcommands:

| Subcommand | Description |
|------------|-------------|
| `list` | List recent sessions. |
| `browse` | Interactive session picker with search and resume. |
| `export <output> [--session-id ID]` | Export sessions to JSONL. |
| `delete <session-id>` | Delete one session. |
| `prune` | Delete old sessions. |
| `stats` | Show session-store statistics. |
| `rename <session-id> <title>` | Set or change a session title. |

## `centurion insights`

```bash
centurion insights [--days N] [--source platform]
```

| Option | Description |
|--------|-------------|
| `--days <n>` | Analyze the last `n` days (default: 30). |
| `--source <platform>` | Filter by source such as `cli`, `telegram`, or `discord`. |

## `centurion claw`

```bash
centurion claw migrate [options]
```

Migrate your OpenClaw setup to Centurion. Reads from `~/.openclaw` (or a custom path) and writes to `~/.centurion`. Automatically detects legacy directory names (`~/.clawdbot`, `~/.moltbot`) and config filenames (`clawdbot.json`, `moltbot.json`).

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview what would be migrated without writing anything. |
| `--preset <name>` | Migration preset: `full` (all compatible settings) or `user-data` (excludes infrastructure config). Neither preset imports secrets — pass `--migrate-secrets` explicitly. |
| `--overwrite` | Overwrite existing Centurion files on conflicts (default: refuse to apply when the plan has conflicts). |
| `--migrate-secrets` | Include API keys in migration. Required even under `--preset full`. |
| `--no-backup` | Skip the pre-migration zip snapshot of `~/.centurion/` (by default a single restore-point archive is written to `~/.centurion/backups/pre-migration-*.zip` before apply; restorable with `centurion import`). |
| `--source <path>` | Custom OpenClaw directory (default: `~/.openclaw`). |
| `--workspace-target <path>` | Target directory for workspace instructions (AGENTS.md). |
| `--skill-conflict <mode>` | Handle skill name collisions: `skip` (default), `overwrite`, or `rename`. |
| `--yes` | Skip the confirmation prompt. |

### What gets migrated

The migration covers 30+ categories across persona, memory, skills, model providers, messaging platforms, agent behavior, session policies, MCP servers, TTS, and more. Items are either **directly imported** into Centurion equivalents or **archived** for manual review.

**Directly imported:** SOUL.md, MEMORY.md, USER.md, AGENTS.md, skills (4 source directories), default model, custom providers, MCP servers, messaging platform tokens and allowlists (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost), agent defaults (reasoning effort, compression, human delay, timezone, sandbox), session reset policies, approval rules, TTS config, browser settings, tool settings, exec timeout, command allowlist, gateway config, and API keys from 3 sources.

**Archived for manual review:** Cron jobs, plugins, hooks/webhooks, memory backend (QMD), skills registry config, UI/identity, logging, multi-agent setup, channel bindings, IDENTITY.md, TOOLS.md, HEARTBEAT.md, BOOTSTRAP.md.

**API key resolution** checks three sources in priority order: config values → `~/.openclaw/.env` → `auth-profiles.json`. All token fields handle plain strings, env templates (`${VAR}`), and SecretRef objects.

For the complete config key mapping, SecretRef handling details, and post-migration checklist, see the **[full migration guide](../guides/migrate-from-openclaw.md)**.

### Examples

```bash
# Preview what would be migrated
centurion claw migrate --dry-run

# Full migration (all compatible settings, no secrets)
centurion claw migrate --preset full

# Full migration including API keys
centurion claw migrate --preset full --migrate-secrets

# Migrate user data only (no secrets), overwrite conflicts
centurion claw migrate --preset user-data --overwrite

# Migrate from a custom OpenClaw path
centurion claw migrate --source /home/user/old-openclaw
```

## `centurion dashboard`

```bash
centurion dashboard [options]
```

Launch the web dashboard — a browser-based UI for managing configuration, API keys, and monitoring sessions. Requires `pip install centurion-ai-os[web]` (FastAPI + Uvicorn). The embedded browser Chat tab requires `--tui` plus the `pty` extra. See [Web Dashboard](/user-guide/features/web-dashboard) for full documentation.

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `9119` | Port to run the web server on |
| `--host` | `127.0.0.1` | Bind address |
| `--no-open` | — | Don't auto-open the browser |
| `--tui` | off | Enable the in-browser Chat tab by running `centurion --tui` behind a PTY/WebSocket bridge. Requires `pip install 'centurion-ai-os[web,pty]'` and a POSIX PTY environment such as Linux, macOS, or WSL2. |
| `--insecure` | off | Allow binding to non-localhost hosts. Exposes dashboard credentials on the network; use only behind trusted network controls. |
| `--stop` | — | Stop running `centurion dashboard` processes and exit. |
| `--status` | — | List running `centurion dashboard` processes and exit. |

```bash
# Default — opens browser to http://127.0.0.1:9119
centurion dashboard

# Custom port, no browser
centurion dashboard --port 8080 --no-open

# Enable the browser Chat tab
centurion dashboard --tui
```

## `centurion profile`

```bash
centurion profile <subcommand>
```

Manage profiles — multiple isolated Centurion instances, each with its own config, sessions, skills, and home directory.

| Subcommand | Description |
|------------|-------------|
| `list` | List all profiles. |
| `use <name>` | Set a sticky default profile. |
| `create <name> [--clone] [--clone-all] [--clone-from <source>] [--no-alias]` | Create a new profile. `--clone` copies config, `.env`, and `SOUL.md` from the active profile. `--clone-all` copies all state. `--clone-from` specifies a source profile. |
| `delete <name> [-y]` | Delete a profile. |
| `show <name>` | Show profile details (home directory, config, etc.). |
| `alias <name> [--remove] [--name NAME]` | Manage wrapper scripts for quick profile access. |
| `rename <old> <new>` | Rename a profile. |
| `export <name> [-o FILE]` | Export a profile to a `.tar.gz` archive (local backup). |
| `import <archive> [--name NAME]` | Import a profile from a `.tar.gz` archive (local restore). |
| `install <source> [--name N] [--alias] [--force] [-y]` | Install a profile distribution from a git URL or local directory. |
| `update <name> [--force-config] [-y]` | Re-pull a distribution; preserves user data (memories, sessions, auth). |
| `info <name>` | Show a profile's distribution manifest (version, requirements, source). |

Examples:

```bash
centurion profile list
centurion profile create work --clone
centurion profile use work
centurion profile alias work --name h-work
centurion profile export work -o work-backup.tar.gz
centurion profile import work-backup.tar.gz --name restored
centurion profile install github.com/user/my-distro --alias
centurion profile update work
centurion -p work chat -q "Hello from work profile"
```

## `centurion completion`

```bash
centurion completion [bash|zsh|fish]
```

Print a shell completion script to stdout. Source the output in your shell profile for tab-completion of Centurion commands, subcommands, and profile names.

Examples:

```bash
# Bash
centurion completion bash >> ~/.bashrc

# Zsh
centurion completion zsh >> ~/.zshrc

# Fish
centurion completion fish > ~/.config/fish/completions/centurion.fish
```

## `centurion update`

```bash
centurion update [--check] [--backup] [--restart-gateway]
```

Pulls the latest `centurion-ai-os` code and reinstalls dependencies in your venv, then re-runs the post-install hooks (MCP servers, skills sync, completion install). Safe to run on a live install.

**pip installs:** `centurion update` detects pip-based installations automatically — it queries PyPI for the latest release and runs `pip install --upgrade centurion-ai-os` instead of `git pull`. PyPI releases track tagged versions (major/minor releases), not every commit on `main`. Use `--check` to see if a newer PyPI release is available without installing.

| Option | Description |
|--------|-------------|
| `--check` | Print the current commit and the latest `origin/main` commit side by side, and exit 0 if in sync or 1 if behind. Does not pull, install, or restart anything. |
| `--backup` | Create a labeled pre-update snapshot of `CENTURION_HOME` (config, auth, sessions, skills, pairing data) before pulling. Default is **off** — the previous always-backup behavior was adding minutes to every update on large homes. Flip it on permanently via `update.backup: true` in `config.yaml`. |
| `--restart-gateway` | After a successful update, restart the running gateway service. Implies `--all` semantics if multiple profiles are installed. |

Additional behavior:

- **Pairing data snapshot.** Even when `--backup` is off, `centurion update` takes a lightweight snapshot of `~/.centurion/pairing/` and the Feishu comment rules before `git pull`. You can roll it back with `centurion backup restore --state pre-update` if a pull rewrites a file you were editing.
- **Legacy `centurion.service` warning.** If Centurion detects a pre-rename `centurion.service` systemd unit (instead of the current `centurion-gateway.service`), it prints a one-time migration hint so you can avoid flap-loop issues.
- **Exit codes.** `0` on success, `1` on pull/install/post-install errors, `2` on unexpected working-tree changes that block `git pull`.

## Maintenance commands

| Command | Description |
|---------|-------------|
| `centurion version` | Print version information. |
| `centurion update` | Pull latest changes and reinstall dependencies. |
| `centurion uninstall [--full] [--yes]` | Remove Centurion, optionally deleting all config/data. |

## See also

- [Slash Commands Reference](./slash-commands.md)
- [CLI Interface](../user-guide/cli.md)
- [Sessions](../user-guide/sessions.md)
- [Skills System](../user-guide/features/skills.md)
- [Skins & Themes](../user-guide/features/skins.md)
