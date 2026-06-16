<p align="center">

```
 ██████╗███████╗███╗   ██╗████████╗██╗   ██╗██████╗ ██╗ ██████╗ ███╗   ██╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗████╗  ██║
██║     █████╗  ██╔██╗ ██║   ██║   ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║
██║     ██╔══╝  ██║╚██╗██║   ██║   ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║
╚██████╗███████╗██║ ╚████║   ██║   ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║
 ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

</p>

# Centurion AI OS

<p align="center">
  <a href="https://github.com/centurion-fleet/Centurion-AI-OS"><img src="https://img.shields.io/badge/Docs-Centurion%20AI%20OS-FFD700?style=for-the-badge" alt="Documentation"></a>
  <a href="https://github.com/centurion-fleet/Centurion-AI-OS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
</p>

**Centurion AI OS** is the self-improving sovereign AI agent — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions. Run it on your own hardware, a $5 VPS, or a GPU cluster. It's not tied to your laptop — talk to it from Telegram while it works on a cloud VM.

Use any model you want — [OpenRouter](https://openrouter.ai) (200+ models), [NovitaAI](https://novita.ai), [NVIDIA NIM](https://build.nvidia.com), [Xiaomi MiMo](https://platform.xiaomimimo.com), [z.ai/GLM](https://z.ai), [Kimi/Moonshot](https://platform.moonshot.ai), [MiniMax](https://www.minimax.io), [Hugging Face](https://huggingface.co), OpenAI, LM Studio, or your own endpoint. Switch with `centurion model` — no code changes, no lock-in.

<table>
<tr><td><b>A real terminal interface</b></td><td>Full TUI with multiline editing, slash-command autocomplete, conversation history, interrupt-and-redirect, and streaming tool output.</td></tr>
<tr><td><b>Lives where you do</b></td><td>Telegram, Discord, Slack, WhatsApp, Signal, and CLI — all from a single gateway process. Voice memo transcription, cross-platform conversation continuity.</td></tr>
<tr><td><b>A closed learning loop</b></td><td>Agent-curated memory with periodic nudges. Autonomous skill creation after complex tasks. Skills self-improve during use. FTS5 session search with LLM summarization for cross-session recall. <a href="https://github.com/plastic-labs/honcho">Honcho</a> dialectic user modeling. Compatible with the <a href="https://agentskills.io">agentskills.io</a> open standard.</td></tr>
<tr><td><b>Scheduled automations</b></td><td>Built-in cron scheduler with delivery to any platform. Daily reports, nightly backups, weekly audits — all in natural language, running unattended.</td></tr>
<tr><td><b>Delegates and parallelizes</b></td><td>Spawn isolated subagents for parallel workstreams. Write Python scripts that call tools via RPC, collapsing multi-step pipelines into zero-context-cost turns.</td></tr>
<tr><td><b>Runs anywhere, not just your laptop</b></td><td>Seven terminal backends — local, Docker, SSH, Singularity, Modal, Daytona, and Vercel Sandbox. Daytona and Modal offer serverless persistence — your agent's environment hibernates when idle and wakes on demand, costing nearly nothing between sessions. Run it on a $5 VPS or a GPU cluster.</td></tr>
<tr><td><b>Research-ready</b></td><td>Batch trajectory generation, trajectory compression for training the next generation of tool-calling models.</td></tr>
</table>

---

## Quick Install

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/centurion-fleet/Centurion-AI-OS/main/scripts/install.sh | bash
```

### Windows (native, PowerShell) — Early Beta

> **Heads up:** Native Windows support is **early beta**. It installs and runs, but hasn't been road-tested as broadly as our Linux/macOS/WSL2 paths. Please [file issues](https://github.com/centurion-fleet/Centurion-AI-OS/issues) when you hit rough edges. For the most battle-tested Windows setup today, run the Linux/macOS one-liner above inside **WSL2**.

Run this in PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/centurion-fleet/Centurion-AI-OS/main/scripts/install.ps1)
```

The installer handles everything: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **and a portable Git Bash** (MinGit, unpacked to `%LOCALAPPDATA%\centurion\git` — no admin required). Centurion AI OS uses this bundled Git Bash to run shell commands.

If you already have Git installed, the installer detects it and uses that instead.  Otherwise a ~45MB MinGit download is all you need — it won't touch or interfere with any system Git.

> **Android / Termux:** See the Termux guide in the docs. On Termux, Centurion AI OS installs a curated `.[termux]` extra because the full `.[all]` extra pulls Android-incompatible voice dependencies.
>
> **Windows:** Native Windows is **early beta**. Native install lives under `%LOCALAPPDATA%\centurion`; WSL2 installs under `~/.centurion` as on Linux. The browser-based dashboard chat pane currently needs WSL2 (POSIX PTY); classic CLI and gateway run natively on Windows.

After installation:

```bash
source ~/.bashrc    # reload shell (or: source ~/.zshrc)
centurion             # start chatting!
```

---

## Getting Started

```bash
centurion              # Interactive CLI — start a conversation
centurion model        # Choose your LLM provider and model
centurion tools        # Configure which tools are enabled
centurion config set   # Set individual config values
centurion gateway      # Start the messaging gateway (Telegram, Discord, etc.)
centurion setup        # Run the full setup wizard (configures everything at once)
centurion claw migrate # Migrate from OpenClaw (if coming from OpenClaw)
centurion update       # Update to the latest version
centurion doctor       # Diagnose any issues
```

---

## Centurion subscription (coming soon)

Centurion AI OS works with your own API keys today — run `centurion setup` and pick OpenRouter, Anthropic, LM Studio, or another provider.

A unified **Centurion Portal** subscription at [portal.personal-centurion.com](https://portal.personal-centurion.com) (models + hosted tools under one plan) is in development. When it launches, enable it in config with `billing.enabled: true` and use `centurion setup --portal`.

---

## CLI vs Messaging Quick Reference

Centurion AI OS has two entry points: start the terminal UI with `centurion`, or run the gateway and talk to it from Telegram, Discord, Slack, WhatsApp, Signal, or Email. Once you're in a conversation, many slash commands are shared across both interfaces.

| Action | CLI | Messaging platforms |
|---------|-----|---------------------|
| Start chatting | `centurion` | Run `centurion gateway setup` + `centurion gateway start`, then send the bot a message |
| Start fresh conversation | `/new` or `/reset` | `/new` or `/reset` |
| Change model | `/model [provider:model]` | `/model [provider:model]` |
| Set a personality | `/personality [name]` | `/personality [name]` |
| Retry or undo the last turn | `/retry`, `/undo` | `/retry`, `/undo` |
| Compress context / check usage | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [days]` |
| Browse skills | `/skills` or `/<skill-name>` | `/<skill-name>` |
| Interrupt current work | `Ctrl+C` or send a new message | `/stop` or send a new message |
| Platform-specific status | `/platforms` | `/status`, `/sethome` |

For the full command lists, run `centurion --help` or see the documentation section below.

---

## Documentation

Centurion AI OS documentation is in progress. Use `centurion --help`, `centurion setup`, and `centurion doctor` to get started. Config and secrets live under `~/.centurion/`.

---

## Migrating from OpenClaw

If you're coming from OpenClaw, Centurion AI OS can automatically import your settings, memories, skills, and API keys.

**During first-time setup:** The setup wizard (`centurion setup`) automatically detects `~/.openclaw` and offers to migrate before configuration begins.

**Anytime after install:**

```bash
centurion claw migrate              # Interactive migration (full preset)
centurion claw migrate --dry-run    # Preview what would be migrated
centurion claw migrate --preset user-data   # Migrate without secrets
centurion claw migrate --overwrite  # Overwrite existing conflicts
```

What gets imported:
- **SOUL.md** — persona file
- **Memories** — MEMORY.md and USER.md entries
- **Skills** — user-created skills → `~/.centurion/skills/openclaw-imports/`
- **Command allowlist** — approval patterns
- **Messaging settings** — platform configs, allowed users, working directory
- **API keys** — allowlisted secrets (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS assets** — workspace audio files
- **Workspace instructions** — AGENTS.md (with `--workspace-target`)

See `centurion claw migrate --help` for all options.

---

## Contributing

We welcome contributions!

Quick start for contributors:

```bash
git clone https://github.com/centurion-fleet/Centurion-AI-OS.git
cd Centurion-AI-OS
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
centurion              # start chatting
```

---

## Community

- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/centurion-fleet/Centurion-AI-OS/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — Linux desktop-control MCP server for agent hosts, with AT-SPI accessibility trees, Wayland/X11 input, screenshots, and compositor window targeting.

---

Built on open-source agent infrastructure. MIT — see [LICENSE](LICENSE).
