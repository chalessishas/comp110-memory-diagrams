# STS2 AI & VTuber Bridge: Latest Developments (March 2026)

**Date**: 2026-03-25
**Purpose**: Competitive landscape scan for the STS2 VTuber Bridge project — AI game agents, MCP gaming integrations, AI VTuber gaming, and related open-source tools.

---

## 1. STS2 AI Agent Ecosystem

### 1a. STS2-Agent (CharTyr) — v0.5.2 (2026-03-18)

- **Source**: [GitHub](https://github.com/CharTyr/STS2-Agent) | [Nexus Mods](https://www.nexusmods.com/slaythespire2/mods/155)
- **What**: Godot mod + MCP server bundle. Exposes full game state and 50+ actions via local HTTP API, wrapped as MCP server for AI clients.
- **Key features in v0.5.2**:
  - Game-data lookup tools, raw state inspection
  - Planner/combat handoff helpers for multi-agent workflows
  - SSE events reduce polling overhead
  - Both stdio and HTTP MCP transport
  - Developer-only `run_console_command` (disabled by default)
- **Relevance**: **Critical** — this is the primary bridge our VTuber project would use. Multi-agent handoff (planner agent for map/deck decisions, combat agent for card play) aligns perfectly with our architecture of having a decision engine feed into a narrator.
- **Actionable**: Our `sts2_client.py` should target v0.5.2 API. The multi-agent handoff API (`get_planner_context`, `create_combat_handoff`, etc.) could replace our custom `decision.py` orchestration.

### 1b. STS2MCP (Gennadiyev)

- **Source**: [GitHub](https://github.com/Gennadiyev/STS2MCP) | [Steam Workshop (MCPTheSpire)](https://steamcommunity.com/sharedfiles/filedetails/?id=3632714834)
- **What**: .NET 9 mod with REST API + optional MCP wrapper. Full game screen coverage including combat, map (DAG with lookahead), shop, events, rest sites, treasure, relic selection.
- **Key differentiators vs STS2-Agent**:
  - Clean REST endpoints (`GET/POST /api/v1/singleplayer`)
  - JSON and Markdown response formats
  - Multiplayer support (per-player voting, relic bidding)
  - Keyword glossary across all entities
  - Runs on port 15526
- **Relevance**: **High** — alternative integration path. The REST API is simpler to prototype against. Multiplayer support is irrelevant for solo VTuber play, but the DAG lookahead for map navigation is valuable for strategic commentary.
- **Actionable**: Could serve as fallback if STS2-Agent has compatibility issues. The Markdown response format is interesting — could pipe directly into narrator prompts without JSON parsing.

### 1c. MCPTheSpire (STS1)

- **Source**: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3632714834)
- **What**: MCP server for Slay the Spire 1. Full MCP protocol via Streamable HTTP transport on `http://127.0.0.1:8080/mcp`. Thread-safe, configurable.
- **Relevance**: **Low** — STS1 only. But confirms the MCP-for-games pattern is maturing.

### 1d. sts2-advisor (ebadon16)

- **Source**: [GitHub](https://github.com/ebadon16/sts2-advisor)
- **What**: Real-time overlay that grades card/relic offerings using community win-rate data. Features static tier data (400+ cards, 150+ relics), deck archetype detection, local learning from your runs, and anonymous community data aggregation.
- **Relevance**: **Medium** — the win-rate data could feed our narrator's commentary ("chat, this card has a 72% win rate in Strength builds..."). C# mod + Cloudflare Worker backend.
- **Actionable**: Explore API access to their aggregated win-rate data for enriching narrator commentary.

### 1e. AgentTheSpire (cgxjdzz)

- **Source**: [GitHub](https://github.com/cgxjdzz/AgentTheSpire)
- **What**: AI-powered STS2 mod generator. Describe a card/relic in plain text, get working C# code + artwork. Uses Claude for code generation, FLUX.2 for image generation, one-click build & deploy.
- **Stack**: Python FastAPI + React/TS frontend + C#/.NET Godot mod template
- **Relevance**: **Low** for VTuber bridge directly, but **interesting** for content creation — the VTuber could narrate the process of AI-generating custom cards during a stream segment.

### 1f. sts-agent (ohylli)

- **Source**: [GitHub](https://github.com/ohylli/sts-agent) | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3643445266)
- **What**: Python toolkit enabling Claude Code to play STS1 via Text the Spire accessibility mod. CLI for reading game state + sending commands.
- **Relevance**: **Medium** — demonstrates Claude-as-player pattern. Their prompt engineering for strategic play (using subagents, stopping for user feedback) is directly applicable to our narrator prompt design.
- **Actionable**: Study their `prompts/video_prompt.md` for inspiration on how to instruct an LLM to narrate gameplay decisions.

---

## 2. STS2 Game Context

- **Release**: Slay the Spire 2 entered Steam Early Access on **March 5, 2026** ([Mega Crit announcement](https://www.megacrit.com/news/2026-02-19-release-date-trailer/))
- **Engine**: Godot (not Java/LibGDX like STS1) — more accessible modding, mods as `.dll` + `.pck`
- **Modding ecosystem**: Active but early. [BaseLib-StS2](https://github.com/Alchyr/BaseLib-StS2) standardizes content additions. Nexus Mods [Upload API](https://www.nexusmods.com/slaythespire2/news/15454) now in open beta.
- **Patch cadence**: Active updates — recent patches addressed infinites being nerfed, game balance changes. Mod compatibility can break with patches.
- **Risk**: Early access = API instability. Our bridge needs graceful degradation when mods break after patches.

---

## 3. MCP Gaming Integrations (Beyond STS2)

The MCP-for-games pattern is expanding rapidly. Sources: [awesome-mcp-servers/gaming.md](https://github.com/TensorBlock/awesome-mcp-servers/blob/main/docs/gaming.md), [aibase Games catalog](https://mcp.aibase.com/class/Games%20and%20gamification)

| Project | Game | What |
|---------|------|------|
| [mcp-minecraft](https://github.com/yuniko-software/minecraft-mcp-server) | Minecraft | Mineflayer-powered, real-time character control via natural language |
| [mcp-gameboy](https://lobehub.com/mcp/arjunkmrm-mcp-minecraft) | GameBoy | LLM interaction with GameBoy emulator, ROM loading + web UI |
| [mcp-chess-poc](https://github.com/TensorBlock/awesome-mcp-servers) | Chess | LLM vs human chess via GUI + MCP |
| [UnityCodeMCPServer](https://github.com/TensorBlock/awesome-mcp-servers) | Unity | Execute C# scripts in Unity Editor via MCP |
| [Godot MCP](https://github.com/TensorBlock/awesome-mcp-servers) | Godot | Edit, run, debug Godot projects via MCP |
| [MCPlayerOne](https://mcpservers.org/servers/SonicDMG/mcp-game-server) | Custom | AI-powered synthwave maze-crawling adventure |
| [mcp-server-runescape](https://github.com/TensorBlock/awesome-mcp-servers) | RuneScape | Item prices, player hiscores |
| [esports-mcp](https://github.com/TensorBlock/awesome-mcp-servers) | LoL | OP.GG esports data for AI agents |

**Relevance**: The Minecraft MCP server is the closest analog to what we're building — an AI controlling a game in real-time with natural language reasoning. Their Mineflayer integration approach (action API + observation stream) is architecturally similar to our STS2 bridge.

**Actionable**: Study mcp-minecraft's architecture for patterns around action throttling, observation batching, and error recovery during gameplay.

---

## 4. AI VTuber Gaming

### 4a. Neuro-sama (Vedal987) — The Benchmark

- **Source**: [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama) | [Vedal AI](https://vedal.ai/)
- **Status**: As of January 2026, **162,459 active Twitch subscribers** — the #1 most subscribed Twitch channel worldwide, ahead of Jynxzi (73,942).
- **Architecture**:
  - **Chat brain**: LLM-based transformer for personality/conversation
  - **Vision**: Separate CV models read game screen → structured text for the LLM brain
  - **Game agents**: Independent per-game AI agents with real-time decision logic (not the LLM)
  - **Voice**: Text-to-Speech synced to Live2D mouth movements
  - **Parallel systems**: Chat AI and game AI run independently
- **Games**: osu!, Minecraft, and others. Game-specific agents are hand-coded, not LLM-driven.
- **Key insight**: Neuro uses **separate specialized game agents** per game, not the LLM for gameplay. The LLM handles personality/chat only.
- **Relevance**: **Critical** — this is both our inspiration and our competition. Our differentiator is using LLM for strategic game decisions (not just chat), which is a harder but more interesting approach.

### 4b. Neuro-sama Game SDK

- **Source**: [GitHub (VedalAI/neuro-game-sdk)](https://github.com/VedalAI/neuro-game-sdk)
- **What**: Official SDK for integrating games with Neuro-sama. Websocket-based API with JSON messages. Official SDKs for Unity and Godot.
- **Optimized for**: Turn-based games where game state fits in text and actions are async — **exactly like STS2**.
- **Recent game integrations (Jan-Feb 2026)**: Buckshot Roulette, Liar's Bar, Inscryption, Cyberpunk
- **Relevance**: **High** — validates the pattern. Their SDK is designed for exactly the type of game STS2 is. We could potentially make our VTuber compatible with this SDK in the future.
- **Actionable**: Study their websocket protocol for game ↔ VTuber communication patterns. The turn-based optimization is directly relevant.

### 4c. Bandai Namco "Play BY Live"

- **Source**: [AUTOMATON WEST](https://automaton-media.com/en/news/20220930-15980/)
- **What**: Bandai Namco's AI VTuber project — corporate effort at AI-driven gaming entertainment.
- **Relevance**: **Low** — older project (2022), but shows industry interest in the space.

---

## 5. LLM Game Agent Research

### 5a. lmgame-Bench (ICLR 2026)

- **Source**: [GitHub](https://github.com/lmgame-org/GamingAgent) | [Paper](https://arxiv.org/abs/2505.15146) | [ICLR 2026 Poster](https://iclr.cc/virtual/2026/poster/10007223)
- **What**: Benchmark for LLM/VLM game-playing agents across 6 games (Sokoban, Tetris, Candy Crush, 2048, Super Mario Bros, Ace Attorney). Modular harness with perception, memory, and reasoning modules.
- **Key finding**: Every game probes a unique blend of capabilities. RL training on Sokoban and Tetris transfers to other games and boosts performance on planning tasks (Blocksworld, WebShop).
- **13 models evaluated** — DeepSeek API integration supported.
- **Relevance**: **High** — provides methodology for evaluating our LLM's STS2 performance. The modular harness (perception/memory/reasoning) maps to our bridge architecture.
- **Actionable**: Consider adding STS2 as a game to this benchmark framework. The modular design could inform our decision.py refactoring.

### 5b. PORTAL: Agents Play Thousands of 3D Games (arXiv 2503.13356)

- **Source**: [Paper](https://arxiv.org/abs/2503.13356)
- **What**: LLMs generate behavior trees in DSL for 3D FPS games. Hybrid policy = rule-based nodes + neural network components. Reduces development from weeks to hours.
- **Relevance**: **Medium** — behavior tree generation via LLM is an interesting pattern. For STS2, a behavior tree could encode deck archetypes and combat heuristics, with LLM handling novel situations.
- **Actionable**: Consider a hybrid approach — use a behavior tree for common STS2 patterns (block when low HP, play damage cards when enemies have low HP) with LLM override for complex decisions.

### 5c. METR: Opus 4.6 CLI Game Reimplementation

- **Source**: [METR Notes](https://metr.org/notes/2026-03-03-balatro-sts-cli/)
- **What**: Claude Opus 4.6 built mostly-playable CLI versions of Slay the Spire and Balatro. STS version cost ~$20, some card effects slightly wrong.
- **Key issues**: Headbutt, Flame Barrier effects wrong; Slimes split at wrong time; Time Eater doesn't eat time.
- **Relevance**: **Medium** — demonstrates Opus's understanding of STS game mechanics, even if imperfect. This is the same model that would power our narrator/decision engine.
- **Actionable**: These known failure modes (incorrect card effect understanding) inform what our game state prompts need to explicitly include — don't rely on the LLM's memory of card effects, always provide current card text.

### 5d. DeepSeek for Game Agents

- **Source**: [DeepSeek V3.2](https://www.deepseek.com/en/)
- **What**: DeepSeek-V3.2 launched — 685B parameters, 128K context, reasoning-first for agents. Integrated with lmgame-Bench.
- **Relevance**: **Medium** — potential alternative to Claude for our decision engine if cost becomes an issue. DeepSeek API is significantly cheaper.
- **Actionable**: Benchmark DeepSeek-V3.2 as decision engine and compare with Claude for STS2 gameplay quality. Could be a cost-effective option for continuous streaming.

---

## 6. Open-LLM-VTuber Updates

- **Source**: [GitHub](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber) | [Docs](http://docs.llmvtuber.com/en/)
- **Latest version**: v1.2.1 (bug fixes on top of v1.2.0)
- **Last repo update**: February 11, 2026
- **v1.2.0 major features**:
  - **MCP support**: AI can call MCP-compatible tools, including BrowserBase Browser Use MCP with Live View in frontend
  - **Letta-based long-term memory** (MemGPT): persistent memory across conversations
  - **Live2D Cubism 5**: Migrated to official Live2D Web SDK (dropped Cubism 2)
  - **Bilibili Danmaku client**: Chinese streaming platform integration
  - **Chinese frontend support**
  - **Status bar for MCP function calls**: visual feedback when AI uses tools
  - **Browser control via Stagehand**: AI can operate a web browser
- **v1.2.1 fixes**: Frontend bug fixes, MCP server argument `cwd` enhancement
- **Open issue [#263](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber/issues/263)**: MCP SSE support requested (currently stdio only)
- **Relevance**: **Critical** — this is our VTuber frontend. The MCP support in v1.2.0 means our STS2 bridge could potentially be an MCP server that Open-LLM-VTuber calls directly, instead of custom websocket integration.
- **Actionable**:
  1. Upgrade our fork to v1.2.1 if not already done
  2. Explore whether our game bridge should be an MCP server that Open-LLM-VTuber connects to natively
  3. The Letta long-term memory could give our VTuber persistent knowledge of past runs ("I remember last time I took this relic and it cost me the run...")

---

## 7. Key Takeaways & Action Items

### Architecture Decision: MCP Chain vs Custom Bridge

Two viable architectures have emerged:

**Option A: MCP Chain** (new possibility from Open-LLM-VTuber v1.2.0)
```
STS2 Game → STS2-Agent (MCP) → Open-LLM-VTuber (MCP client) → LLM → Voice/Avatar
```
- Pro: Native integration, less custom code
- Con: May be too slow for real-time narration, limited control over decision/narration separation

**Option B: Custom Bridge** (current approach)
```
STS2 Game → STS2-Agent (HTTP API) → game_bridge/bridge.py → decision.py + narrator.py → Open-LLM-VTuber
```
- Pro: Full control over decision timing, narration style, multi-agent orchestration
- Con: More code to maintain

**Recommendation**: Stick with Option B but use STS2-Agent's MCP multi-agent handoff API to simplify decision.py. Use Open-LLM-VTuber's MCP support for auxiliary tools (browser for looking up strategies, etc.) but keep the core game loop custom.

### Priority Actions

1. **Pin STS2-Agent v0.5.2** as our target API version
2. **Adopt STS2-Agent's multi-agent handoff** (`get_planner_context` / `create_combat_handoff`) instead of reimplementing orchestration
3. **Always include card text in prompts** — don't rely on LLM memory (per METR findings)
4. **Study Neuro-sama Game SDK** protocol for inspiration on our VTuber ↔ game communication
5. **Evaluate DeepSeek-V3.2** as cost-effective alternative for continuous streaming
6. **Leverage sts2-advisor win-rate data** for enriching narrator commentary
7. **Upgrade to Open-LLM-VTuber v1.2.1** and enable Letta memory for cross-run continuity

### Competitive Landscape Summary

| What | Who | Threat Level |
|------|-----|-------------|
| AI VTuber playing games | Neuro-sama | High (but uses hand-coded game agents, not LLM) |
| LLM playing STS2 via MCP | STS2-Agent users | Medium (no VTuber/streaming layer) |
| LLM game benchmarks | lmgame-Bench | None (academic, complementary) |
| AI mod generation for STS2 | AgentTheSpire | None (different problem space) |

**Our unique position**: LLM-driven strategic gameplay + VTuber narration + streaming. Nobody else is combining all three for STS2 specifically.

---

## Sources

- [STS2-Agent (CharTyr) — GitHub](https://github.com/CharTyr/STS2-Agent)
- [STS2-Agent — Nexus Mods](https://www.nexusmods.com/slaythespire2/mods/155)
- [STS2MCP (Gennadiyev) — GitHub](https://github.com/Gennadiyev/STS2MCP)
- [MCPTheSpire — Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3632714834)
- [AgentTheSpire — GitHub](https://github.com/cgxjdzz/AgentTheSpire)
- [sts-agent (ohylli) — GitHub](https://github.com/ohylli/sts-agent)
- [sts2-advisor — GitHub](https://github.com/ebadon16/sts2-advisor)
- [Neuro-sama — Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama)
- [Neuro Game SDK — GitHub](https://github.com/VedalAI/neuro-game-sdk)
- [lmgame-Bench — ICLR 2026](https://arxiv.org/abs/2505.15146)
- [GamingAgent — GitHub](https://github.com/lmgame-org/GamingAgent)
- [PORTAL: Agents Play 3D Games — arXiv](https://arxiv.org/abs/2503.13356)
- [METR: Opus STS/Balatro CLI](https://metr.org/notes/2026-03-03-balatro-sts-cli/)
- [Open-LLM-VTuber — GitHub](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)
- [Open-LLM-VTuber v1.2.0 Release Notes](http://docs.llmvtuber.com/en/blog/v1.2.0-release/)
- [Open-LLM-VTuber v1.2.1 Release](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber/releases/tag/v1.2.1)
- [awesome-mcp-servers Gaming List](https://github.com/TensorBlock/awesome-mcp-servers/blob/main/docs/gaming.md)
- [MCP 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [STS2 Early Access Announcement](https://www.megacrit.com/news/2026-02-19-release-date-trailer/)
- [DeepSeek V3.2](https://www.deepseek.com/en/)
- [Slay the Spire 2 Patch Notes](https://www.gamewatcher.com/news/slay-the-spire-2-patch-notes-roadmap-of-updates)

---

## Addendum: Research Loop 2 (15:10)

增量搜索，聚焦具体技术细节。

### 人类 A20 胜率基线（我们 AI 的对标）
- Ironclad: 50-75% (高手), Silent: 40-60%, Defect: 46-65%, Watcher: 72-96%
- 核心洞察："A20 胜利不是靠构筑好牌组，而是靠解决眼前致命问题"
- **对 AI 的启示**: prompt 需要强调当前回合的生存问题，而非长期 deck building 规划
- 来源: [Steam 社区讨论](https://steamcommunity.com/app/646570/discussions/0/644693912552869526/), [GameHelper A20 指南](https://www.gamehelper.io/games/slay-the-spire/articles/slay-the-spire-guide-perfecting-your-ascension-climb)

### LLM 玩 STS 胜率数据
- **无公开数据**。截至 2026-03-25，没有任何团队发布过 LLM 玩 STS1/STS2 的胜率基准
- 这是一个差异化机会：如果我们的 AI 能在 A0 达到 >50% 胜率并公开数据，可以获得社区关注

### DeepSeek V3.2 性能
- AIME 96.0%（超 GPT-5 的 94.6%），数学推理强
- 无专门的游戏策略 benchmark，但强推理能力对卡牌决策有利
- 来源: [DeepSeek V3.2 分析](https://artificialanalysis.ai/models/deepseek-v3-2-0925)

### Open-LLM-VTuber 版本线
- v1.2.1 是当前最新稳定版（我们用的）
- v1.3.0 预计改 license（Apache 2.0 变体），功能待定
- v1.2.0 关键特性：MCP 原生支持、Letta 长期记忆、Live2D Cubism 5、Bilibili 弹幕
- 来源: [v1.2.0 发布说明](http://docs.llmvtuber.com/en/blog/v1.2.0-release/), [v1.2.1 Release](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber/releases/tag/v1.2.1)
