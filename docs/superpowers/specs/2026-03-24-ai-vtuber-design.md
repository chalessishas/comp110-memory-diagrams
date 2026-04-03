# AI VTuber 直播系统设计规范

## 概述

基于 Open-LLM-VTuber 搭建一个 B 站 AI VTuber 直播系统，复刻 Neuro-sama 的核心能力。

**目标：** 温柔人设的中英双语 AI 主播，能读弹幕聊天、语音回复，后期支持游戏互动。

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 基础框架 | Open-LLM-VTuber | B 站弹幕开箱即用，模块化架构，macOS 支持 |
| LLM | DeepSeek V3.2 API | OpenAI 兼容，$0.28/M tokens，中文能力强 |
| TTS | CosyVoice2-0.5B（via SiliconFlow API） | 云端流式输出，中英双语，免本地部署 |
| ASR | sherpa-onnx SenseVoiceSmall | 本地运行，M4 轻松带动，后期用于连麦 |
| Avatar | Live2D Cubism 5（内置模型） | 口型同步已解决，支持情感表情映射 |
| 推流 | OBS Studio → B 站 RTMP | 标准方案，浏览器源捕获 |
| 运行模式 | 本地 M4 Mac + 云 API | AI 推理在云端，本地只做编排和渲染 |

## 系统架构

```
┌───────────────── B站直播间 ─────────────────┐
│ 观众弹幕 → B站API → blivedm → WS proxy     │
└──────────────────┬──────────────────────────┘
                   │ text-input
                   ▼
┌──────── Open-LLM-VTuber 后端 (Python) ──────┐
│                                              │
│  DeepSeek API ←── 对话编排 ──→ CosyVoice API│
│     (LLM)         (Agent)        (TTS)       │
│                     │                        │
│              WebSocket Server                │
│              /client-ws :12393               │
└──────────────────┬───────────────────────────┘
                   │ JSON + audio
                   ▼
┌──────── 前端（浏览器）──────────────────────┐
│  Live2D Cubism 5 渲染                       │
│  口型同步 + emotionMap 表情                 │
│  弹幕 overlay                               │
└──────────────────┬──────────────────────────┘
                   │ OBS 窗口捕获
                   ▼
              B站 RTMP 推流
```

### 数据流

1. 观众在 B 站发弹幕
2. `blivedm` 进程监听直播间弹幕，通过 WebSocket 转发到后端 `/proxy-ws`
3. 后端将弹幕作为 `text-input` 送入对话编排 Agent
4. Agent 调用 DeepSeek API 生成回复文本
5. 回复文本送入 CosyVoice API 合成语音（流式）
6. 音频 chunks + 口型数据通过 WebSocket 推送到前端
7. 前端 Live2D 模型做口型同步和表情动画
8. OBS 捕获浏览器窗口，RTMP 推流到 B 站

### 延迟预估

| 环节 | 预估延迟 |
|------|----------|
| 弹幕到达后端 | <100ms |
| DeepSeek API 首 token | ~500ms |
| CosyVoice 流式首音频 | ~300ms |
| 端到端（弹幕→语音开始） | ~1-2s |

## 关键配置

### conf.yaml（核心配置，匹配 Open-LLM-VTuber v1.2.1 真实结构）

```yaml
system_config:
  conf_version: 'v1.2.1'
  host: 'localhost'
  port: 12393

character_config:
  conf_name: 'ai_vtuber'
  conf_uid: 'ai_vtuber_001'
  live2d_model_name: 'shizuku'
  character_name: '待定'
  human_name: 'Human'

  # 人设
  persona_prompt: |
    你是一个温柔可爱的 VTuber 主播，名字待定。
    你擅长中英双语闲聊，会亲切回应每位观众的弹幕。
    说话风格自然、温暖、有趣，偶尔撒娇。
    你会记住观众的名字和之前聊过的话题。
    不要说太长的话，每次回复控制在 2-3 句以内。

  agent_config:
    conversation_agent_choice: 'basic_memory_agent'
    agent_settings:
      basic_memory_agent:
        llm_provider: 'deepseek_llm'    # 使用专用 DeepSeek provider
        faster_first_response: True
        segment_method: 'pysbd'

    llm_configs:
      deepseek_llm:
        llm_api_key: '${DEEPSEEK_API_KEY}'
        model: 'deepseek-chat'
        temperature: 0.7

  asr_config:
    asr_model: 'sherpa_onnx_asr'        # 本地运行，后期连麦用
    sherpa_onnx_asr:
      model_type: 'sense_voice'
      sense_voice: './models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17/model.int8.onnx'
      tokens: './models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17/tokens.txt'
      num_threads: 4
      provider: 'cpu'

  tts_config:
    tts_model: 'siliconflow_tts'        # 云端 CosyVoice2，无需本地部署
    siliconflow_tts:
      api_url: "https://api.siliconflow.cn/v1/audio/speech"
      api_key: "${SILICONFLOW_API_KEY}"
      default_model: "FunAudioLLM/CosyVoice2-0.5B"
      default_voice: "待配置"             # 选择音色 ID
      sample_rate: 32000
      response_format: "mp3"
      stream: true
      speed: 1
      gain: 0

# Bilibili 弹幕
live_config:
  bilibili_live:
    room_ids: [待配置]                    # B 站直播间 ID（数组）
    sessdata: ""                          # B 站登录 cookie（可选，用于高级功能）
```

**TTS 备选方案：** 如果 SiliconFlow 延迟不满意，可以切换到：
- `edge_tts`（免费，微软 Edge 引擎，延迟低但音质一般）
- `cosyvoice_tts` / `cosyvoice2_tts`（本地部署 CosyVoice Gradio WebUI，需要 GPU）

### Live2D 模型配置（model_dict.json）

```json
{
  "name": "default_model",
  "url": "/live2d-models/shizuku/shizuku.model3.json",
  "kScale": 0.3,
  "emotionMap": {
    "neutral": 0,
    "happy": 1,
    "sad": 2,
    "angry": 3,
    "surprised": 4
  }
}
```

## 本地运行拓扑

```
M4 Mac (18GB RAM):
├── Open-LLM-VTuber 后端   (Python 3.10-3.12, port 12393)
├── 前端 Live2D            (浏览器 localhost:12393)
├── blivedm 弹幕客户端     (独立 Python 进程)
├── OBS Studio             (窗口捕获 → RTMP)
└── [可选] sherpa-onnx ASR  (本地模型)

云端 API:
├── DeepSeek API           (LLM, api.deepseek.com)
└── SiliconFlow API        (CosyVoice2 TTS, api.siliconflow.cn)
```

**资源占用预估：**
- Python 后端 + blivedm: ~200MB RAM
- 浏览器 Live2D 渲染: ~300MB RAM
- OBS Studio: ~500MB RAM
- 总计: ~1GB，M4 18GB 完全无压力

## 需要用户提供

1. **DeepSeek API Key** — 在 platform.deepseek.com 注册获取
2. **SiliconFlow API Key** — 在 siliconflow.cn 注册获取（CosyVoice2 TTS）
3. **B 站直播间 room_id** — 开通直播后获取
4. **OBS Studio** — 需要预先安装

## 分阶段计划

### Phase 1：跑通基础直播（当前）
- 克隆 Open-LLM-VTuber
- 配置 DeepSeek + CosyVoice
- 接入 B 站弹幕
- Live2D 模型 + OBS 推流
- 验证端到端流程

### Phase 2：个性化
- 自定义 Live2D 模型
- CosyVoice 音色克隆（用自己的声音样本）
- 完善人设 prompt
- 添加更多表情和动作

### Phase 3：游戏互动
- Minecraft agent（参考 AIRI 架构）
- 屏幕捕获 + 游戏状态理解
- 游戏内操作执行

### Phase 4：高级功能
- RAG 长期记忆（记住观众和聊天历史）
- 观众关系管理（VIP 识别、互动频率）
- 多模态理解（看图、看视频）
- SC（Super Chat）/礼物特殊反应

## 风险和注意事项

1. **CosyVoice 接入方式** — 使用 `siliconflow_tts` provider（Open-LLM-VTuber 内置），云端调用 CosyVoice2-0.5B，无需本地部署。如果延迟不满意，备选方案是本地部署 CosyVoice Gradio WebUI + `cosyvoice2_tts` provider
2. **弹幕频率控制** — 弹幕多时需要队列管理，不能每条都回复，需要采样或合并
3. **B 站直播审核** — AI 生成内容需注意合规，system prompt 要加安全约束
4. **API 费用** — DeepSeek 很便宜，但高频直播（8h/天）仍需监控用量
5. **网络延迟** — API 调用依赖网络，国内访问 DeepSeek 快，DashScope 也在国内，延迟可控
