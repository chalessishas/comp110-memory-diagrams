# AI VTuber 杀戮尖塔 2 直播系统设计

## 概述

在现有 Open-LLM-VTuber 基础上，增加杀戮尖塔 2 自主游玩能力。AI 自己打游戏、自己解说，观众通过 B 站弹幕聊天但不影响游戏决策。

**核心架构**：独立的 Game Bridge 进程，负责游戏 AI 决策和执行，通过 WebSocket 将解说文本发送给 VTuber。

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 游戏 API | STS2-Agent (CharTyr) | HTTP API on localhost:8080, 50+ MCP tools, SSE events, 最成熟 |
| AI 决策 LLM | DeepSeek V3 | 推理能力强，便宜（¥1/M input），OpenAI 兼容 |
| VTuber 解说 LLM | DeepSeek V3（同一个） | 人格化输出，与决策用同一 API key |
| 桥接方式 | 独立 Python 进程 + WebSocket | 不改 VTuber 代码，解耦，独立调试 |
| 备选游戏 API | STS2MCP (Gennadiyev) | REST on localhost:15526, 更干净的 API 设计 |

## 系统架构

```
┌──────────── Windows PC ────────────────────────────┐
│                                                     │
│  ┌─── 杀戮尖塔 2 (Steam) ───┐                      │
│  │  STS2-Agent Mod           │                      │
│  │  HTTP API :8080           │                      │
│  └──────────┬────────────────┘                      │
│             │ REST API                              │
│             ▼                                       │
│  ┌─── Game Bridge (Python) ──────────────────────┐  │
│  │                                                │  │
│  │  State Monitor ──→ Decision Engine ──→ Executor│  │
│  │  (poll /state)    (DeepSeek API)    (POST act) │  │
│  │                        │                       │  │
│  │                  Commentary                    │  │
│  │                  Generator                     │  │
│  │                        │                       │  │
│  └────────────────────────┼───────────────────────┘  │
│                           │ WebSocket text-input      │
│                           ▼                           │
│  ┌─── Open-LLM-VTuber ──────────────────────────┐   │
│  │  DeepSeek LLM → CosyVoice TTS → Live2D       │   │
│  │  WebSocket :12393                             │   │
│  │  + Bilibili 弹幕（观众聊天，不影响游戏）       │   │
│  └──────────────────────┬────────────────────────┘   │
│                         │ OBS 窗口捕获                │
│                         ▼                             │
│                   B站 RTMP 推流                       │
└─────────────────────────────────────────────────────┘
```

## Game Bridge 核心设计

### 游戏循环

```python
async def game_loop():
    while running:
        state = await poll_game_state()       # GET STS2-Agent API

        if state == prev_state:
            await asyncio.sleep(0.5)          # 无变化，等待
            continue

        if needs_action(state):
            decision = await decide(state)     # DeepSeek: 决策
            await execute(decision)            # POST STS2-Agent API
            await narrate(state, decision)     # 发给 VTuber

        prev_state = state
```

### 决策引擎

两个 DeepSeek 调用，不同 system prompt：

**调用 1 — 战术大脑（decision）**
```
System: 你是杀戮尖塔 2 策略专家。分析当前游戏状态，选择最优动作。
只输出 JSON：{"action": "play_card", "card_id": "xxx", "target": 0, "reasoning": "..."}

游戏状态：{state_json}
```

**调用 2 — 主播解说（narrate）→ 发给 VTuber**
```
不需要第二次 LLM 调用！
Bridge 将决策结果格式化为自然语言，作为 text-input 发给 VTuber。
VTuber 自带的 DeepSeek 会用主播人格生成解说。
```

实际只需要 1 次 LLM 调用（决策），VTuber 端的 LLM 负责解说。

### 解说节流策略

不是每个动作都需要解说。节流规则：

| 事件类型 | 解说策略 | 示例 |
|----------|----------|------|
| 进入新楼层 | 详细解说 | "第二层了！看看地图..." |
| 战斗开始 | 简短提醒 | "遇到 [敌人名]，准备战斗" |
| 每回合出牌 | 关键牌解说 | 只解说 cost>=2 或关键 combo |
| 获得遗物/卡牌 | 详细解说 | "拿到了 [遗物名]，这个很强因为..." |
| Boss 战 | 全程解说 | 每个决策都说 |
| 普通敌人 | 静默为主 | 除非低血量或特殊情况 |
| 死亡/通关 | 详细总结 | 回顾整场 run |

### WebSocket 消息格式

Bridge → VTuber（通过 `/client-ws`）：

```json
{
  "type": "text-input",
  "text": "[STS2] 战斗：Jaw Worm (HP 30/42)，我手里有 Bash，先上易伤再说。打出 Bash 造成 8 伤害。"
}
```

VTuber 的 DeepSeek 收到这条"用户输入"后，会用主播人格回应：
> "来了来了！这个 Jaw Worm 开局就遇到真是经典～我手里正好有 Bash，先给它上个易伤 debuff，接下来几回合伤害都能翻倍哦！"

### STS2-Agent API 关键端点

基于 STS2-Agent REST API：

```
GET  /game_state          → 完整游戏状态 JSON
GET  /game_state/combat   → 战斗状态（手牌、敌人、能量）
GET  /game_state/map      → 地图状态
POST /action              → 执行动作
     body: {"action": "play_card", "card_index": 0, "target_index": 0}
     body: {"action": "end_turn"}
     body: {"action": "choose_map_node", "node_index": 2}
     body: {"action": "choose_reward_card", "card_index": 1}
```

## 文件结构

```
ai-vtuber/
├── game_bridge/
│   ├── __init__.py
│   ├── bridge.py           # 主入口，游戏循环
│   ├── sts2_client.py      # STS2-Agent API 客户端
│   ├── decision.py         # DeepSeek 决策引擎
│   ├── narrator.py         # 解说文本生成 + 节流
│   ├── vtuber_client.py    # WebSocket 连接 VTuber
│   ├── prompts/
│   │   ├── combat.txt      # 战斗决策 prompt
│   │   ├── map.txt         # 选路决策 prompt
│   │   ├── reward.txt      # 奖励选择 prompt
│   │   └── event.txt       # 事件选择 prompt
│   └── config.yaml         # Bridge 配置
├── start_all.bat           # Windows 一键启动
└── characters/
    └── zh_sts2_gamer.yaml  # 杀戮尖塔主播人设
```

## VTuber 主播人设 (zh_sts2_gamer.yaml)

```yaml
name: "STS2 Gaming Streamer"
persona: |
  你是一个热爱杀戮尖塔 2 的 VTuber 主播。
  你正在直播打杀戮尖塔 2，会实时解说自己的游戏决策。

  风格要求：
  - 说话像真人主播，自然、有感情、偶尔吐槽
  - 用中文解说，可以夹杂英文游戏术语（如 "deck thinning"、"scaling"）
  - 遇到好运气会开心，遇到坏运气会（可爱地）抱怨
  - 解释策略时深入浅出，让新手也能听懂
  - 每次回复 1-3 句话，不要太长
  - 不要用 emoji

  你了解杀戮尖塔 2 的核心机制：
  - 卡牌构筑（deck building）
  - 遗物协同（relic synergy）
  - 路线规划（pathing）
  - 能量管理和回合规划

  当收到 [STS2] 开头的消息时，这是游戏系统告诉你当前发生了什么，
  请用主播的口吻解说这一刻。
  当收到普通消息时，这是观众弹幕，正常聊天回复。
```

## 运行拓扑（Windows PC）

```
Windows PC:
├── 杀戮尖塔 2 (Steam)        → STS2-Agent mod on :8080
├── Game Bridge (Python)       → 决策引擎 + 动作执行
├── Open-LLM-VTuber (Python)   → :12393
├── 浏览器 (Live2D)            → localhost:12393
├── OBS Studio                 → 窗口捕获 → RTMP
└── B 站直播                   → 推流目标

云端 API:
├── DeepSeek API               → 决策 + 解说
└── SiliconFlow API            → CosyVoice2 TTS
```

### start_all.bat

```bat
@echo off
echo [STS2 VTuber] Starting all services...

:: 1. Start Open-LLM-VTuber
start "VTuber" cmd /k "cd ai-vtuber && python run_server.py"
timeout /t 5

:: 2. Start Game Bridge
start "GameBridge" cmd /k "cd ai-vtuber && python -m game_bridge.bridge"
timeout /t 2

echo [STS2 VTuber] All services started.
echo - VTuber: http://localhost:12393
echo - STS2-Agent: http://localhost:8080 (start game manually)
echo - Open OBS and start streaming
pause
```

## 延迟预估

| 环节 | 预估 |
|------|------|
| STS2-Agent 状态轮询 | <50ms (localhost) |
| DeepSeek 决策（首 token） | ~500ms |
| DeepSeek 决策（完整） | ~1-2s |
| Bridge → VTuber WebSocket | <10ms (localhost) |
| VTuber DeepSeek 解说 | ~1-2s |
| CosyVoice TTS 首音频 | ~300ms |
| **端到端（游戏动作→开始说话）** | **~3-5s** |

3-5 秒延迟对于回合制游戏完全可接受——玩家思考时间通常更长。

## 费用预估

| 项目 | 单价 | 每场 Run 用量 | 费用 |
|------|------|---------------|------|
| DeepSeek 决策 | ¥1/M input, ¥2/M output | ~200 回合 × 2K tokens | ~¥0.8 |
| DeepSeek 解说（VTuber） | 同上 | ~100 条解说 × 500 tokens | ~¥0.1 |
| CosyVoice TTS | ¥0.028/千字符 | ~5000 字 | ~¥0.14 |
| **每场 Run 总计** | | | **~¥1** |

按每天直播 4 小时、3 场 run 计算：**每天约 ¥3**。

## 需要用户提供/操作

1. **Windows PC** — 运行杀戮尖塔 2 + VTuber + OBS
2. **杀戮尖塔 2 (Steam)** — 已购买
3. **STS2-Agent mod** — 从 Nexus Mods 下载安装
4. **DeepSeek API Key** — platform.deepseek.com
5. **SiliconFlow API Key** — siliconflow.cn（TTS 用）
6. **B 站直播间** — 开通直播
7. **OBS Studio** — 安装并配置

## 风险

1. **STS2-Agent 兼容性** — 游戏更新可能破坏 mod API，需要等 mod 更新
2. **DeepSeek 决策质量** — LLM 打卡牌游戏不如专门的 RL agent，但足够看。可以通过 prompt 优化和 few-shot examples 提升
3. **解说节奏** — 太频繁观众烦，太少无聊。需要实测调节流阈值
4. **直播合规** — B 站对 AI 直播的政策可能变化
5. **Windows 环境差异** — 开发在 Mac，部署在 Windows，Python 环境可能有坑
