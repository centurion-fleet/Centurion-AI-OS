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
  <a href="https://github.com/centurion-fleet/Centurion-AI-OS"><img src="https://img.shields.io/badge/Docs-Centurion%20AI%20OS-FFD700?style=for-the-badge" alt="文档"></a>
  <a href="https://github.com/centurion-fleet/Centurion-AI-OS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="许可证: MIT"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-English-lightgrey?style=for-the-badge" alt="English"></a>
</p>

**Centurion AI OS** 是自进化的主权 AI 代理——从经验中创建技能，在使用中改进技能，主动持久化知识，搜索过往对话，并在跨会话中逐步构建对你的深度理解。可在自有硬件、$5 VPS 或 GPU 集群上运行。不绑定笔记本——在 Telegram 上对话，它在云端 VM 上工作。

支持任意模型——[OpenRouter](https://openrouter.ai)（200+ 模型）、[NovitaAI](https://novita.ai)、[NVIDIA NIM](https://build.nvidia.com)、[小米 MiMo](https://platform.xiaomimimo.com)、[z.ai/GLM](https://z.ai)、[Kimi/Moonshot](https://platform.moonshot.ai)、[MiniMax](https://www.minimax.io)、[Hugging Face](https://huggingface.co)、OpenAI、LM Studio 或自定义端点。使用 `centurion model` 即可切换——无需改代码，无锁定。

<table>
<tr><td><b>真正的终端界面</b></td><td>完整的 TUI，支持多行编辑、斜杠命令自动补全、对话历史、中断重定向和流式工具输出。</td></tr>
<tr><td><b>随你所在</b></td><td>Telegram、Discord、Slack、WhatsApp、Signal 和 CLI——全部从单个网关进程运行。语音备忘录转写、跨平台对话连续性。</td></tr>
<tr><td><b>闭环学习</b></td><td>代理管理记忆并定期自我提醒。复杂任务后自动创建技能。技能在使用中自我改进。FTS5 会话搜索配合 LLM 摘要实现跨会话回溯。<a href="https://github.com/plastic-labs/honcho">Honcho</a> 辩证式用户建模。兼容 <a href="https://agentskills.io">agentskills.io</a> 开放标准。</td></tr>
<tr><td><b>定时自动化</b></td><td>内置 cron 调度器，支持向任何平台投递。日报、夜间备份、周审计——全部用自然语言描述，无人值守运行。</td></tr>
<tr><td><b>委派与并行</b></td><td>生成隔离子代理处理并行工作流。编写 Python 脚本通过 RPC 调用工具，将多步管道压缩为零上下文开销的轮次。</td></tr>
<tr><td><b>随处运行</b></td><td>七种终端后端——本地、Docker、SSH、Singularity、Modal、Daytona 和 Vercel Sandbox。Daytona 和 Modal 提供 Serverless 持久化——代理环境空闲时休眠、按需唤醒，空闲期间几乎零成本。$5 VPS 或 GPU 集群都能跑。</td></tr>
<tr><td><b>研究就绪</b></td><td>批量轨迹生成、轨迹压缩，用于训练下一代工具调用模型。</td></tr>
</table>

---

## 快速安装

### Linux、macOS、WSL2、Termux

```bash
curl -fsSL https://raw.githubusercontent.com/centurion-fleet/Centurion-AI-OS/main/scripts/install.sh | bash
```

### Windows（原生 PowerShell）——早期测试版

> **提示：** 原生 Windows 支持为**早期测试版**。可安装运行，但不如 Linux/macOS/WSL2 路径成熟。遇到问题请[提交 issue](https://github.com/centurion-fleet/Centurion-AI-OS/issues)。最稳妥的 Windows 方案是在 **WSL2** 中运行上述 Linux/macOS 一键安装命令。

在 PowerShell 中运行：

```powershell
iex (irm https://raw.githubusercontent.com/centurion-fleet/Centurion-AI-OS/main/scripts/install.ps1)
```

安装程序会处理一切：uv、Python 3.11、Node.js、ripgrep、ffmpeg，以及**便携式 Git Bash**（MinGit，解压到 `%LOCALAPPDATA%\centurion\git`，无需管理员权限）。Centurion AI OS 使用此捆绑的 Git Bash 运行 shell 命令。

若已安装 Git，安装程序会检测并使用。否则只需约 45MB 的 MinGit 下载——不会干扰系统 Git。

> **Android / Termux：** 请参阅文档中的 Termux 指南。Termux 上 Centurion AI OS 安装精选的 `.[termux]` 额外依赖，因为完整的 `.[all]` 会拉取 Android 不兼容的语音依赖。
>
> **Windows：** 原生 Windows 为**早期测试版**。原生安装位于 `%LOCALAPPDATA%\centurion`；WSL2 安装位于 `~/.centurion`，与 Linux 相同。基于浏览器的仪表板聊天面板目前需要 WSL2（POSIX PTY）；经典 CLI 和网关在 Windows 上可原生运行。

安装后：

```bash
source ~/.bashrc    # 重新加载 shell（或：source ~/.zshrc）
centurion             # 开始对话！
```

---

## 入门

```bash
centurion              # 交互式 CLI——开始对话
centurion model        # 选择 LLM 提供商和模型
centurion tools        # 配置启用的工具
centurion config set   # 设置单个配置值
centurion gateway      # 启动消息网关（Telegram、Discord 等）
centurion setup        # 运行完整设置向导（一次性配置所有内容）
centurion claw migrate # 从 OpenClaw 迁移（如适用）
centurion update       # 更新到最新版本
centurion doctor       # 诊断问题
```

---

## Centurion 订阅（即将推出）

Centurion AI OS 目前可使用你自己的 API 密钥——运行 `centurion setup` 并选择 OpenRouter、Anthropic、LM Studio 或其他提供商。

统一的 **Centurion Portal** 订阅（[portal.personal-centurion.com](https://portal.personal-centurion.com)——模型 + 托管工具合一）正在开发中。上线后，在配置中设置 `billing.enabled: true` 并使用 `centurion setup --portal`。

---

## CLI 与消息平台快速参考

Centurion AI OS 有两个入口：用 `centurion` 启动终端 UI，或运行网关后从 Telegram、Discord、Slack、WhatsApp、Signal 或 Email 对话。进入对话后，许多斜杠命令在两个界面通用。

| 操作 | CLI | 消息平台 |
|---------|-----|---------------------|
| 开始对话 | `centurion` | 运行 `centurion gateway setup` + `centurion gateway start`，然后给机器人发消息 |
| 新对话 | `/new` 或 `/reset` | `/new` 或 `/reset` |
| 切换模型 | `/model [provider:model]` | `/model [provider:model]` |
| 设置人格 | `/personality [name]` | `/personality [name]` |
| 重试或撤销上一轮 | `/retry`、`/undo` | `/retry`、`/undo` |
| 压缩上下文 / 查看用量 | `/compress`、`/usage`、`/insights [--days N]` | `/compress`、`/usage`、`/insights [days]` |
| 浏览技能 | `/skills` 或 `/<skill-name>` | `/<skill-name>` |
| 中断当前工作 | `Ctrl+C` 或发送新消息 | `/stop` 或发送新消息 |
| 平台特定状态 | `/platforms` | `/status`、`/sethome` |

完整命令列表请运行 `centurion --help` 或参阅下方文档。

---

## 文档

Centurion AI OS 文档正在完善中。使用 `centurion --help`、`centurion setup` 和 `centurion doctor` 入门。配置和密钥位于 `~/.centurion/`。

---

## 从 OpenClaw 迁移

若从 OpenClaw 迁移，Centurion AI OS 可自动导入设置、记忆、技能和 API 密钥。

**首次设置期间：** 设置向导（`centurion setup`）会自动检测 `~/.openclaw` 并在配置前提供迁移选项。

**安装后随时：**

```bash
centurion claw migrate              # 交互式迁移（完整预设）
centurion claw migrate --dry-run    # 预览将迁移的内容
centurion claw migrate --preset user-data   # 迁移但不包含密钥
centurion claw migrate --overwrite  # 覆盖现有冲突
```

导入内容：
- **SOUL.md** — 人格文件
- **记忆** — MEMORY.md 和 USER.md 条目
- **技能** — 用户创建的技能 → `~/.centurion/skills/openclaw-imports/`
- **命令允许列表** — 审批模式
- **消息设置** — 平台配置、允许用户、工作目录
- **API 密钥** — 白名单密钥（Telegram、OpenRouter、OpenAI、Anthropic、ElevenLabs）
- **TTS 资源** — 工作区音频文件
- **工作区指令** — AGENTS.md（使用 `--workspace-target`）

参见 `centurion claw migrate --help` 了解所有选项。

---

## 贡献

欢迎贡献！

贡献者快速开始：

```bash
git clone https://github.com/centurion-fleet/Centurion-AI-OS.git
cd Centurion-AI-OS
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
centurion              # 开始对话
```

---

## 社区

- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/centurion-fleet/Centurion-AI-OS/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — 用于代理主机的 Linux 桌面控制 MCP 服务器，支持 AT-SPI 无障碍树、Wayland/X11 输入、截图和合成器窗口定位。

---

基于开源代理基础设施构建。MIT — 见 [LICENSE](LICENSE)。
