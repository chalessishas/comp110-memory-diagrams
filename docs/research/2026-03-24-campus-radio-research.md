# Signal-Map 校园电台功能调研

**日期:** 2026-03-24
**项目:** Signal-Map (hdmap.live)
**状态:** 调研完成，待执行

---

## 1. CC0/免版权音乐源

### 核心发现

**HoliznaCC0 (Free Music Archive)** 是最佳选择。该艺术家专门制作 CC0 1.0 Universal 授权的 lofi/chill 音乐，完全公共领域，无需署名，可直接下载 MP3。已有多张专辑：

| 专辑 | 风格 | 适合时段 |
|------|------|----------|
| [Lo-fi And Chill](https://freemusicarchive.org/music/holiznacc0/lo-fi-and-chill) | lofi hip-hop | daytime, evening |
| [Public Domain Lofi](https://freemusicarchive.org/music/holiznacc0/public-domain-lofi) | lofi chill | night, evening |
| [Winter Lofi](https://freemusicarchive.org/music/holiznacc0/winter-lofi) | 冬季氛围 lofi | night |
| [Background Music](https://freemusicarchive.org/music/holiznacc0/background-music) | 通用背景 | morning, daytime |

**Pixabay Music** 是备选方案。139+ 首 lofi 曲目，免费下载无需署名，但许可证不是 CC0 而是 Pixabay 自有的 Content License，商用安全但条款不如 CC0 干净。

### 对项目的建议

1. **立即执行：** 从 HoliznaCC0 下载 16-20 首曲目（每时段 4-5 首），放入 `public/radio/{morning,daytime,evening,night}/`
2. **选曲策略：** morning 选节奏稍快的（Background Music 专辑），night 选最柔和的（Winter Lofi），daytime/evening 选中等节奏（Lo-fi And Chill）
3. **文件大小：** 每首 2-4MB（128kbps MP3），20 首总计约 50-80MB，Vercel 免费方案允许
4. **manifest.json** 当前为空数组，下载后需手动填充曲目元数据

### 来源
- [HoliznaCC0 - Free Music Archive](https://freemusicarchive.org/music/holiznacc0/)
- [Pixabay Lofi Music](https://pixabay.com/music/search/lofi/)
- [HoliznaCC0 Bandcamp](https://holiznacc0.bandcamp.com/album/lofi-and-chill)

---

## 2. DashScope qwen3-tts-flash 实际体验

### 核心发现

**延迟表现优秀。** qwen3-tts-flash 首包延迟低至 97ms（实测可达 86ms），远优于 ElevenLabs (~200ms) 和 OpenAI TTS (~150ms)。支持 Dual-Track 混合流式架构，合成速度达实时的 5 倍。

**质量对比：** 在 WER（词错误率）指标上优于 ElevenLabs 9% 和 OpenAI 20%。语音相似度评分 0.789 vs ElevenLabs 的 0.646。但纯英语自然度方面，ElevenLabs 仍然更好——Qwen3-TTS 的英语偶尔有轻微的机械感。

**当前实现的问题：** 项目当前使用非流式 API（一次性返回 audio URL），这意味着用户要等完整合成完才能听到。对于 60 词的电台播报（约 15-20 秒音频），等待时间约 2-3 秒，可接受但不理想。

### 对项目的建议

1. **短期：** 当前非流式方案够用。60 词播报文案合成时间 < 3 秒，用户体验可接受
2. **中期优化：** 切换到 DashScope 实时流式 API (`stream=True`)，将首音频延迟降到 ~100ms。需要改 `synthesizeSpeech()` 返回流而非 URL
3. **Voice 选择：** 当前用 "Ethan"，建议试试不同时段用不同 voice（morning 用活泼的，night 用柔和的）
4. **成本：** DashScope qwen3-tts-flash 定价极低（约 ¥0.01/千字），校园电台场景几乎零成本

### 来源
- [Qwen3-TTS-Flash Review (Analytics Vidhya)](https://www.analyticsvidhya.com/blog/2025/12/qwen3-tts-flash-review/)
- [Qwen3-TTS vs ElevenLabs (qwen3-tts.app)](https://qwen3-tts.app/blog/qwen3-tts-vs-elevenlabs-openai-comparison-2026)
- [Qwen3-TTS 97ms Latency (gaga.art)](https://gaga.art/blog/qwen3-tts/)
- [DashScope 实时语音合成文档](https://www.alibabacloud.com/help/en/model-studio/qwen-tts-realtime)
- [Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS)

---

## 3. 校园电台类产品竞品

### 核心发现

**没有直接竞品。** 搜索未发现将"校园活动地图 + AI 电台"结合的产品。这是一个差异化优势。

**最接近的项目：**
- **RadioGPT (Futuri Media):** 世界首个 AI 驱动的本地化电台平台，用 GPT-3 + TopicPulse 自动生成播报，但面向商业电台而非校园
- **Endless LUP (Lupe Fiasco + MIT):** 全 AI FM 电台，说唱歌手与 MIT 合作，但偏娱乐/实验性质
- **GHQ.fm (University of Florida):** 佛罗里达大学正在测试 AudioAI for Radio，但更偏向传统校园广播的 AI 辅助，不是 web-native 的

**UNESCO World Radio Day 2026 主题就是 "Radio and AI"**，说明这个方向正在被广泛关注。

### 对项目的建议

1. **定位独特性：** "基于真实校园事件数据的 AI 电台" 是独特卖点，没有竞品做到事件感知的播报
2. **功能差异化：** 播报内容直接关联地图上的事件（已实现），这比通用 AI 电台更有价值
3. **潜在参考：** RadioGPT 的 TopicPulse 概念（实时话题追踪 → 自动生成内容）可以借鉴——未来可加入天气、校园新闻

### 来源
- [RadioGPT - AI Radio (RouteNote)](https://routenote.com/blog/a-fully-ai-powered-radio-station-in-2025/)
- [GHQ.fm - AudioAI for Radio (UF)](https://ghq.wuft.org/about-ai-for-radio/)
- [World Radio Day 2026 (RedTech)](https://www.redtech.pro/world-radio-day-2026-artificial-intelligence/)
- [AI in Radio Broadcasting (radio.co)](https://www.radio.co/blog/how-to-use-ai-in-radio-broadcasting)

---

## 4. Web Audio API 移动端已知坑

### 核心发现

**iOS Safari 是最大问题。** 三个关键限制：

1. **Autoplay 被完全阻止：** 必须有用户交互（click/tap）才能播放音频。当前 `RadioPlayer` 要求用户点击播放按钮，这是正确的做法
2. **后台播放直接停止：** iOS Safari 切到后台/锁屏时会暂停 Web Audio。这是 WebKit 架构限制（[Bug 198277](https://bugs.webkit.org/show_bug.cgi?id=198277)），2025 年仍未修复。**没有可靠的纯 web 绕过方案**
3. **AudioContext 挂起：** `new Audio()` 创建后如果不是在用户手势回调中 `.play()`，AudioContext 会处于 `suspended` 状态

**Android Chrome 限制更宽松：** autoplay 仍需用户交互，但后台播放在某些条件下可以继续。

### 对项目的建议

1. **必须修复 — AudioContext 初始化：** 当前 `handleTogglePlay()` 在用户点击时调用 `audio.play()`，这是正确的。但 `playNext()` 中的自动播下一首可能触发 autoplay 限制。建议在首次用户点击时调用 `audioRef.current.play()` 来"预热" Audio 对象
2. **后台播放提示：** 在 UI 中提示"锁屏后音频将暂停"，这是 Safari 的限制无法绕过
3. **使用 `<audio>` HTML 标签替代 `new Audio()`：** Safari 对 HTML `<audio>` 标签的后台播放支持稍好于纯 JS Audio 对象。将 `audioRef` 改为引用一个隐藏的 `<audio>` 元素
4. **Media Session API：** 添加 `navigator.mediaSession` 元数据，让锁屏界面显示曲目信息和播放控制按钮
5. **错误恢复：** `audio.play()` 返回 Promise，当 reject 时应该设置 `isPlaying = false` 并显示"点击继续播放"

```tsx
// 建议在 RadioPlayer 中添加 Media Session 支持
if ('mediaSession' in navigator && currentTrack) {
  navigator.mediaSession.metadata = new MediaMetadata({
    title: currentTrack.title,
    artist: currentTrack.artist,
    album: 'Campus Radio',
  });
  navigator.mediaSession.setActionHandler('play', () => handleTogglePlay());
  navigator.mediaSession.setActionHandler('pause', () => handleTogglePlay());
  navigator.mediaSession.setActionHandler('nexttrack', () => playNextTrackRef.current());
}
```

### 来源
- [MDN Autoplay Guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay)
- [WebKit Bug 198277 - Background Audio](https://bugs.webkit.org/show_bug.cgi?id=198277)
- [iOS AudioContext Warmup Gist](https://gist.github.com/kus/3f01d60569eeadefe3a1)
- [Navigator.getAutoplayPolicy() - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/getAutoplayPolicy)

---

## 5. Vercel Edge Runtime + Streaming TTS

### 核心发现

**完全可行。** Vercel Edge Functions 自 2025 年 3 月起支持最长 300 秒的流式响应。只要 25 秒内开始发送首个字节，之后可以持续流式传输。这完美匹配 TTS 流式场景。

**DashScope 支持流式输出。** qwen3-tts-flash 的 DashScope API 支持 `stream=True` 参数，返回 async generator 的音频 chunks。可以将这些 chunks 直接通过 Edge Function 的 `ReadableStream` 转发给客户端。

**AI SDK 5 已支持 speech：** Vercel 的 AI SDK 5 扩展了统一 provider 抽象到 speech 领域，但目前支持的 provider 是 OpenAI/ElevenLabs/DeepGram，不包括 DashScope。需要自己写适配器或直接用原始 API。

### 对项目的建议

1. **短期不需要改：** 当前的非流式方案（`/api/radio/announce` → 返回 audioUrl）对 60 词播报够用。DashScope 返回的 URL 有效期 24 小时，客户端直接播放
2. **中期升级路径：** 如果未来要做更长的 TTS（比如新闻摘要、长文朗读），流式方案值得投入：

```
用户请求 → Edge Function → DashScope stream API → TransformStream → 客户端 MediaSource
```

3. **Edge vs Serverless 选择：** 当前 `announce/route.ts` 用的是 `dynamic = "force-dynamic"` 的 Serverless Function。它还调用了 Prisma（查事件），而 Edge Runtime 不支持标准 Prisma Client。**不建议把 announce 路由迁到 Edge**。如果要做流式 TTS，应该拆成两个路由：
   - `/api/radio/announce` — Serverless: 生成文案 + 返回文本
   - `/api/radio/tts` — Edge: 接收文本 → 流式调用 DashScope → 流式返回音频

4. **客户端播放流式音频：** 需要 `MediaSource` API 或直接用 `<audio src="blob:...">` + Blob 拼接。Mobile Safari 对 MediaSource 支持有限，fallback 到非流式更安全

### 来源
- [Vercel Streaming Functions](https://vercel.com/docs/functions/streaming-functions)
- [Vercel Edge Runtime Docs](https://vercel.com/docs/functions/runtimes/edge)
- [Edge Functions 300s Duration Limit](https://vercel.com/changelog/new-execution-duration-limit-for-edge-functions)
- [Vercel AI SDK 5](https://vercel.com/blog/ai-sdk-5)
- [DashScope 实时语音合成](https://www.alibabacloud.com/help/en/model-studio/qwen-tts-realtime)

---

## 综合优先级建议

| 优先级 | 任务 | 原因 |
|--------|------|------|
| P0 | 下载 HoliznaCC0 音乐填充 manifest.json | 电台无音乐无法工作 |
| P0 | 配置 Vercel 环境变量 (DEEPSEEK_API_KEY, DASHSCOPE_API_KEY) | 生产环境播报功能依赖 |
| P1 | 添加 Media Session API | 改善移动端体验，锁屏显示播放控制 |
| P1 | 将 `new Audio()` 改为隐藏 `<audio>` 标签 | 改善 Safari 兼容性 |
| P2 | 不同时段使用不同 TTS voice | 增强氛围感 |
| P2 | 添加 autoplay 失败的 UI 提示 | 移动端用户体验 |
| P3 | 流式 TTS (Edge Function + DashScope stream) | 当前场景非必须，长文案时再做 |
