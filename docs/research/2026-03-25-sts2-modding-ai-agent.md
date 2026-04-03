# Slay the Spire 2: Modding & AI Agent Ecosystem Research

**Date**: 2026-03-25
**Purpose**: Evaluate whether an AI agent can programmatically play Slay the Spire 2 via existing mods/APIs.

---

## 1. STS2 Modding Support — Current State

**Engine**: STS2 runs on **Godot Engine** (not Unity/Java like STS1). This is a significant change.

**Official support**: Steam Workshop is the primary mod distribution channel, officially supported by the developers.

**Advanced modding**: BepInEx mod loader is available for deeper/experimental mods. Mods are distributed as `.dll` + `.pck` files placed in the game's `mods/` directory.

**Key libraries**:
- [BaseLib-StS2](https://github.com/Alchyr/BaseLib-StS2) — Standardized base for content addition mods
- [BetterSpire2](https://www.nexusmods.com/slaythespire2/mods/2) — QoL mod framework

**Maturity**: Active but early — mod compatibility can break with official patches. Community is growing on Nexus Mods and GitHub.

---

## 2. AI-Accessible Mods for STS2 (REST/MCP APIs)

### 2a. STS2-Agent (CharTyr) — BEST OPTION

- **Repo**: https://github.com/CharTyr/STS2-Agent
- **Nexus**: https://www.nexusmods.com/slaythespire2/mods/155
- **Architecture**: Godot mod (DLL) → HTTP API on `127.0.0.1:8080` → MCP server wrapper
- **Transport**: Supports both stdio MCP and HTTP MCP
- **SSE events** reduce polling overhead

**MCP Tools (50+ tools across 3 profiles: guided/layered/full)**:

| Category | Tools |
|----------|-------|
| State inspection | `get_game_state`, `get_raw_game_state`, `get_available_actions`, `health_check` |
| Game data lookup | `get_game_data_item`, `get_game_data_items`, `get_relevant_game_data` |
| Combat actions | `play_card`, `end_turn`, `use_potion`, `discard_potion` |
| Map/progression | `choose_map_node`, `proceed`, `open_chest`, `choose_treasure_relic` |
| Events/rest | `choose_event_option`, `choose_rest_option` |
| Shop | `open_shop_inventory`, `close_shop_inventory`, `buy_card`, `buy_relic`, `buy_potion`, `remove_card_at_shop` |
| Rewards | `claim_reward`, `choose_reward_card`, `skip_reward_cards`, `collect_rewards_and_proceed` |
| Card selection | `select_deck_card`, `confirm_modal`, `dismiss_modal` |
| Run management | `continue_run`, `abandon_run`, `select_character`, `embark`, `open_timeline` |
| Multi-agent | `get_planner_context`, `create_planner_handoff`, `get_combat_context`, `create_combat_handoff`, `complete_combat_handoff`, `append_combat_knowledge`, `append_event_knowledge` |
| Async | `wait_for_event`, `wait_until_actionable` |
| Debug | `run_console_command` (opt-in via env var) |

### 2b. STS2MCP (Gennadiyev) — ALTERNATIVE

- **Repo**: https://github.com/Gennadiyev/STS2MCP
- **Architecture**: C# DLL (.NET 9 SDK) → HTTP API on `127.0.0.1:15526` → optional MCP wrapper
- **Formats**: JSON and Markdown response formats

**REST API Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /api/v1/singleplayer?format=json` | GET | Full game state |
| `POST /api/v1/singleplayer` | POST | Execute actions |
| `GET /api/v1/multiplayer` | GET | Multiplayer state |
| `POST /api/v1/multiplayer` | POST | Multiplayer actions |

**Available POST actions**:
- `play_card` (card_index, target)
- `use_potion` (slot, target)
- `end_turn`
- `combat_select_card` / `combat_confirm_selection`
- `claim_reward` (index)
- `select_card_reward` / `skip_card_reward`
- `proceed`
- `choose_rest_option` (index)
- `shop_purchase` (index)
- `choose_event_option` (index)
- `choose_map_node` (index)
- `select_card` / `confirm_selection` / `cancel_selection`
- `select_relic` / `skip_relic_selection`
- `claim_treasure_relic` (index)
- `advance_dialogue`

**Game state `state_type` values**: monster, elite, boss, hand_select, combat_rewards, card_reward, map, rest_site, shop, event, card_select, relic_select, treasure, overlay, menu

**Multiplayer extras**: per-player ready/vote tracking, end_turn voting, map node voting, relic bidding

**Coverage**: Combat, rewards, map (full DAG with lookahead), rest sites, shop, events, ancients, card selection overlays (transform/upgrade/remove), relic selection, treasure rooms, keyword glossary.

---

## 3. Game State Data Available

From both STS2 mods and the STS1 CommunicationMod, the following data is programmatically accessible:

### Combat State
- **Hand**: Cards with name, id, cost, type, is_playable, has_target, uuid, upgrades
- **Draw pile, Discard pile, Exhaust pile**: Full card lists
- **Monsters/Enemies**: name, current_hp, max_hp, block, intent, move_base_damage
- **Player**: current_hp, max_hp, block, energy, powers/buffs/debuffs, orbs
- **Turn number**, cards_discarded_this_turn, times_damaged

### Run State
- **Deck**: Full card collection
- **Relics**: Owned relics with counters
- **Potions**: Available potion slots and contents
- **Gold**: Currency
- **Map**: Node-based DAG with symbol, x, y, parents, children (with lookahead in STS2MCP)
- **Floor, Act, Ascension level, Character class**
- **Room type, Room phase, Action phase**
- **Seed**: Run seed value

### Screen/UI State
- Screen type (combat, map, shop, event, rest, rewards, etc.)
- Available commands/actions for current context

---

## 4. Available Programmatic Actions

| Category | Actions |
|----------|---------|
| Combat | Play card (with targeting), End turn, Use potion, Discard potion |
| Navigation | Choose map node, Proceed to next screen |
| Rewards | Claim reward, Choose/skip card reward, Collect and proceed |
| Card management | Select card for transform/upgrade/remove, Confirm/cancel selection |
| Shop | Open/close shop, Buy card/relic/potion, Remove card |
| Events | Choose event option, Advance dialogue |
| Rest sites | Choose rest option (rest/smith/etc.) |
| Relics | Choose/skip relic selection, Claim treasure relic |
| Treasure | Open chest |
| Run management | Start/continue/abandon run, Select character, Embark |

---

## 5. AI Playing Slay the Spire — Existing Projects

### STS2 (Slay the Spire 2)

| Project | Type | URL |
|---------|------|-----|
| **STS2-Agent** | MCP server + HTTP API mod | https://github.com/CharTyr/STS2-Agent |
| **STS2MCP** | REST API mod + optional MCP | https://github.com/Gennadiyev/STS2MCP |
| **sts2-advisor** | Real-time AI overlay (win-rate data) | https://github.com/ebadon16/sts2-advisor |
| **AgentTheSpire** | AI that generates STS2 mods (cards/relics) | https://github.com/cgxjdzz/AgentTheSpire |

### STS1 (Slay the Spire 1)

| Project | Type | URL |
|---------|------|-----|
| **CommunicationMod** | stdin/stdout protocol for external control | https://github.com/ForgottenArbiter/CommunicationMod |
| **spirecomm** | Python package for CommunicationMod + simple AI | https://github.com/ForgottenArbiter/spirecomm |
| **sts-agent** | Claude Code plays STS1 via Text the Spire | https://github.com/ohylli/sts-agent |
| **bottled_ai** | Automated STS1 gameplay bot | https://github.com/xaved88/bottled_ai |
| **BattleAIMod** | Autobattler: AI fights, you build deck | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2848752403) |
| **MiniSTS** | Simplified STS for RL/LLM experimentation | https://github.com/iambb5445/MiniSTS |

### Academic Research

| Paper | Finding | URL |
|-------|---------|-----|
| **Language-Driven Play (FDG 2024)** | LLMs show superior long-term planning in STS without specialized training, but aren't optimal for single-move decisions | https://dl.acm.org/doi/10.1145/3649921.3650013 |
| **LLMs as Game Difficulty Testers** | LLM agents correlate with human difficulty perception in STS challenges | https://arxiv.org/html/2410.02829v1 |
| **METR CLI Reimplementation (2026)** | Opus 4.6 built a mostly-playable CLI STS clone in one session (~$20 cost), with some card effect bugs | https://metr.org/notes/2026-03-03-balatro-sts-cli/ |
| **3-hour LLM Bot** | Claude Haiku played STS1, reached Act 2 boss | https://gigazine.net/gsc_news/en/20240506-slay-the-spire-llm-bot/ |

---

## 6. Recommendations

**For playing STS2 with AI right now**: **STS2-Agent** is the most mature option. It provides:
- Full MCP integration (works directly with Claude Desktop / Claude Code)
- 50+ tools covering every game screen
- Multi-agent workflow support (planner/combat handoff)
- SSE events for efficient state monitoring
- Active development

**STS2MCP** is a solid alternative if you prefer a clean REST API with explicit endpoints and want JSON/Markdown format flexibility.

**For STS1**: CommunicationMod + spirecomm is the established standard with years of community use.
