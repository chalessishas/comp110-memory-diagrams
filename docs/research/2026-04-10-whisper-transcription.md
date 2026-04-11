# Whisper Transcription Research — 2026-04-10

**Context:** The main agent just transcribed an 87-minute English lecture (96 MB .mp4) on a Darwin 24.6.0 Apple Silicon Mac using `faster-whisper==1.2.1` with the `small` + `int8` model, Silero VAD, and aggressive anti-hallucination params (`no_speech_threshold=0.85`, `log_prob_threshold=-0.8`, `compression_ratio_threshold=1.8`, `condition_on_previous_text=False`). The run hit 0.25× realtime on CPU (~4× faster than realtime). Residual issues: (1) a ~82-second hallucination window in a silent board-writing stretch still slipped past the strict params and had to be patched via a post-hoc delete+marker script; (2) `small` model English WER is good but not great; (3) faster-whisper on CPU may be suboptimal on Apple Silicon because CTranslate2 has no Metal backend. This report evaluates whether to switch backend and how to harden the pipeline against hallucinations for future lecture/meeting jobs.

## Q1: faster-whisper vs openai-whisper (2025 state)

**Speed.** faster-whisper remains the go-to optimized runtime in 2025. Its core advantage — the CTranslate2 C++ runtime with INT8/FP16 quantization — still delivers roughly **4× the speed of openai-whisper at the same accuracy, with lower memory use** (SYSTRAN README, 2025). Nothing in the 2025 release cadence has closed that gap: openai-whisper itself is largely dormant as a reference implementation, and optimization work has migrated to faster-whisper, WhisperX, insanely-fast-whisper, and MLX-Whisper. A Modal.com blog comparing variants concludes that all forks share identical model weights, so **accuracy is effectively tied when decoding settings match** — you choose based on runtime, not WER.

**Memory.** faster-whisper with INT8 roughly halves RAM vs openai-whisper FP32. On the current `small` + int8 config the working set is ~0.5–1 GB, which is why it runs comfortably on CPU. Switching to `large-v3` would still fit in ~3–4 GB with int8 but latency scales roughly 5–6×.

**2025 notable changes.** faster-whisper added batched inference (PR #856) and native Silero-VAD v5 support (PR #936). openai-whisper added nothing substantive in 2025. The ecosystem consensus: **keep faster-whisper as the Python-side API** if you stay on CUDA/CPU; only move off it for Apple Silicon acceleration reasons (Q2).

Sources: [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper), [Modal — Choosing between Whisper variants](https://modal.com/blog/choosing-whisper-variants), [Baseten — fastest Whisper transcription](https://www.baseten.co/blog/the-fastest-most-accurate-and-cost-efficient-whisper-transcription/).

## Q2: Apple Silicon backend shootout

The critical finding: **faster-whisper on Apple Silicon is CPU-only. It has no Metal backend and the SYSTRAN maintainers have stated it is not planned** ([faster-whisper #325](https://github.com/guillaumekln/faster-whisper/issues/325), [discussion #1227](https://github.com/SYSTRAN/faster-whisper/discussions/1227)). That means the current setup is leaving the GPU and the 38-TOPS Neural Engine completely idle.

### Benchmark data (2025–2026)

| Backend | Accel path | Model | Relative speed |
|---|---|---|---|
| `faster-whisper` | CPU only | small/int8 | baseline (current 0.25× RT) |
| `whisper.cpp` | Metal + CoreML (encoder on ANE) | large-v3-turbo q5_0 | ~3× faster than CPU-only whisper.cpp; ~26.7 s mean for the turbo test suite |
| `mlx-whisper` | Metal (MLX) | large-v3-turbo | **~2.0× faster than whisper.cpp** (13.1 s vs 26.7 s mean, `2.03 ± 0.06×`) |
| `lightning-whisper-mlx` | MLX + batching | large | claims 10× whisper.cpp, 4× baseline mlx-whisper |

On an M2 Ultra, mlx-whisper with `large-v3-turbo` transcribed 12 minutes of audio in **14 seconds (~50× realtime)** — the main agent's current `small`/int8 on CPU is 4× realtime, so **the speed headroom on Apple Silicon is roughly 10–15×** before you even go to a bigger model. Voicci's M-series table shows even `medium` on M3/M4 runs at 0.08–0.15× RTF using optimized backends.

Key interpretation for the main agent's hardware (M-series, exact chip unspecified):

- **MLX-Whisper is currently the fastest general-purpose backend** on Apple Silicon for models ≥ small. Install is one line: `pip install mlx-whisper`. CLI and Python API both exist. It is no longer experimental — it has been stable since 2024 and is in production use.
- **whisper.cpp with CoreML** is a strong runner-up. It needs a one-time CoreML encoder compilation (slow first run, then cached). Good if you want a C++ binary with no Python dependency. 3× over CPU-only, but still half the speed of mlx-whisper on turbo.
- **Lightning-Whisper-MLX** claims 4× over mlx-whisper via batching, but it hasn't been updated for large-v3-turbo and the 10× whisper.cpp claim comes from a single author benchmark. Treat as experimental; do not adopt for production lecture workflows yet.
- **Accuracy.** All three backends load the same Whisper weights. WER is identical when decoding params (beam size, temperature, VAD) are held constant. Hallucination behavior is also fork-agnostic — it is a model property, not a runtime property.

### Verdict on backend switch

Switching from `faster-whisper (CPU, small/int8)` to `mlx-whisper (large-v3-turbo)` should give **simultaneous ~4–6× speedup AND substantial accuracy gain** (large-v3-turbo is within 1–2% WER of full large-v3, and clearly better than `small`). This is the highest-ROI change in the whole report.

Sources: [llimllib — MLX vs whisper.cpp Jan 2026](https://notes.billmill.org/dev_blog/2026/01/updated_my_mlx_whisper_vs._whisper.cpp_benchmark.html), [Voicci — Apple Silicon Whisper benchmarks](https://www.voicci.com/blog/apple-silicon-whisper-performance.html), [mustafaaljadery/lightning-whisper-mlx](https://github.com/mustafaaljadery/lightning-whisper-mlx), [mlx-whisper on PyPI](https://pypi.org/project/mlx-whisper/), [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp), [Oliver Wehrens — M1/M2/M3 MLX benchmarks](https://owehrens.com/whisper-nvidia-rtx-4090-vs-m1pro-with-mlx/).

## Q3: Long-audio + anti-hallucination best practices (2025)

### Model choice for accuracy

`whisper-large-v3-turbo` (released Sep 2024) is the new default for long-form English. It has 32 encoder layers but only 4 decoder layers (vs 32 in large-v3), giving **~6× speedup over large-v3 while staying within 1–2% WER** of the full model ([OpenAI HF card](https://huggingface.co/openai/whisper-large-v3-turbo), [Amgad Hasan — Demystifying Whisper Turbo](https://amgadhasan.substack.com/p/demystifying-openais-new-whisper)). It is multilingual and well-supported in mlx-whisper, whisper.cpp, and faster-whisper.

For English-only workloads, `distil-large-v3.5` is ~1.5× faster than turbo, within ~1% WER on short-form and slightly behind on long-form. For the agent's lecture use case turbo is a safer pick (multilingual fallback, stable behavior on long audio, better HF model maturity).

### Hallucination mitigation — what actually works in 2025

Layer these in order of effort vs payoff:

1. **VAD pre-segmentation with Silero v5 or pyannote.** This is the single biggest win. WhisperX's VAD-first pipeline reduces hallucinations and enables batched 70× realtime transcription. **Silero v5 is fast and CPU-friendly but has known v5 regressions** where some quiet dialog gets dropped; pyannote is 3.8× throughput vs Silero's 2× in WhisperX benchmarks and has better edge handling. For the agent's lecture case (mostly speech with silent board-writing stretches), **pyannote is the safer choice** — the 82-s hallucination window happened because Silero leaked a silent region into the ASR. Pyannote's segment merging is less likely to misclassify quiet writing as speech.

2. **Use `stable-ts` parameters on top of faster-whisper or mlx-whisper.** The `stable-ts` library exposes:
   - `suppress_silence=True` and `suppress_ts_tokens=True` — drops timestamp tokens at silent sections
   - `nonspeech_skip` — explicitly skips non-speech ranges given by a VAD
   - `avg_prob_threshold` — **discards any segment whose average word logprob falls below the threshold** (e.g. 0.6). This is the automatic in-band hallucination filter the main agent asked about: you don't need a post-hoc scanner, `stable-ts` drops hallucinated segments during decoding.

3. **Calm-Whisper fine-tuned checkpoints** (arXiv 2505.12969, May 2025). The paper found that just **3 of 20 self-attention heads in Whisper-large-v3's decoder account for >75% of non-speech hallucinations**, and fine-tuning only those three heads on non-speech audio paired with blank labels cut non-speech hallucinations by >80% with <0.1% WER degradation on LibriSpeech. A drop-in Calm-Whisper checkpoint exists; loading it in place of `large-v3` through stable-ts is a near-free upgrade if an MLX conversion is available. If not, it's a ~1-hour conversion job.

4. **Bag of Hallucinations (BoH)** + delooping (arXiv 2501.11378). Detects repeated n-grams that characterize Whisper loops and suppresses them at decode time. Already partially implemented in faster-whisper's `compression_ratio_threshold` — the agent already has this tuned to 1.8 which is on the strict side.

5. **Chunked transcription for multi-hour files.** For anything >30 minutes: (a) chunk at VAD boundaries so splits never fall mid-utterance; (b) use 2–5 s overlap between chunks; (c) run each chunk with `condition_on_previous_text=False` to prevent cross-chunk drift. WhisperX handles all of this automatically. mlx-whisper's built-in chunking is 30-s fixed window — good enough for lectures but WhisperX's VAD-aware chunking is superior.

### Automatic in-stream hallucination detection

The answer to "can we detect during transcription, not post-hoc" is **yes, via `stable-ts`'s `avg_prob_threshold`** and Whispy's repeating-token filter. Neither requires a second pass. Both integrate with faster-whisper and (via a thin adapter) with mlx-whisper.

Sources: [Calm-Whisper arXiv](https://arxiv.org/abs/2505.12969), [Investigation of Whisper hallucinations arXiv 2501.11378](https://arxiv.org/html/2501.11378v1), [m-bain/whisperX](https://github.com/m-bain/whisperX), [jianfch/stable-ts](https://github.com/jianfch/stable-ts), [snakers4/silero-vad](https://github.com/snakers4/silero-vad), [huggingface/distil-whisper](https://github.com/huggingface/distil-whisper).

## Recommendations for transcribe.py v2 (ranked by ROI)

1. **[HIGHEST ROI] Switch backend to `mlx-whisper` with `large-v3-turbo`.** Install: `pip install mlx-whisper`. Replace the `WhisperModel("small", compute_type="int8")` call with `mlx_whisper.transcribe(audio, path_or_hf_repo="mlx-community/whisper-large-v3-turbo")`. Expected impact: **~4–6× speedup** (0.25× RT → ~0.05× RT, i.e. an 87-min lecture in ~4 min instead of ~22 min) AND noticeable accuracy gain from small → large-v3-turbo (WER roughly cut in half on real-world English). Effort: **~30 minutes** including retesting on the same lecture. This single change dominates everything else.

2. **[HIGH ROI] Replace Silero VAD with pyannote VAD in the preprocessing step.** Pyannote 3.1 is better at edges of silent stretches and is what WhisperX defaults to. This directly addresses the 82-second board-writing hallucination the agent hit. Effort: **~45 minutes** (pyannote needs an HF token for model download, then a simple call returns speech timestamps; feed them as `clip_timestamps` to the transcriber). If HF auth becomes a pain, fall back to Silero v5 with `min_silence_duration_ms=1000` to force longer silent drops.

3. **[HIGH ROI] Add `stable-ts` as the decoding wrapper with `avg_prob_threshold=0.6`, `suppress_silence=True`, `nonspeech_skip=True`.** This auto-drops low-confidence segments mid-decode, eliminating the need for the post-hoc delete+marker patch script. `stable-ts` wraps both openai-whisper and faster-whisper cleanly; the mlx-whisper wrapper is a thin shim. Effort: **~1 hour** including param tuning on the known-bad lecture.

4. **[MEDIUM ROI] Switch to WhisperX architecture for long files (>45 min).** Instead of one big transcribe call, do: pyannote VAD → chunk at boundaries with 3-s overlap → batched transcribe → stitch. Gives 70× RT claims with word-level timestamps almost for free. Effort: **~2 hours**, but mostly replaces existing code so net complexity stays flat. Do this only if mlx-whisper's built-in chunking still misbehaves after recs 1–3.

5. **[LOW-MED ROI] Evaluate Calm-Whisper checkpoint.** If an MLX conversion of Calm-Whisper-large-v3 exists on HuggingFace, drop it in as `path_or_hf_repo`. If not, convert via `mlx_whisper.convert`. Effort: **~1 hour if a conversion exists, ~3 hours if not**. Only pursue if recs 1–3 still leave residual hallucinations.

6. **[LOW ROI] Keep a faster-whisper fallback path.** Keep `transcribe.py` able to run on machines without MLX (Linux servers, non-Apple hardware). Structure as a backend enum with `mlx` as default and `faster-whisper` as fallback. Effort: **~30 minutes**. Cheap insurance.

## References

- [SYSTRAN/faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper) — canonical faster-whisper source, 2025 releases, no Metal backend.
- [Modal — Choosing between Whisper variants](https://modal.com/blog/choosing-whisper-variants) — clarifies that all forks share identical weights and accuracy.
- [Baseten — fastest Whisper transcription 2025](https://www.baseten.co/blog/the-fastest-most-accurate-and-cost-efficient-whisper-transcription/) — hosted benchmark numbers.
- [llimllib — mlx_whisper vs whisper.cpp Jan 2026 update](https://notes.billmill.org/dev_blog/2026/01/updated_my_mlx_whisper_vs._whisper.cpp_benchmark.html) — the key data point: mlx-whisper 2.03× whisper.cpp on large-v3-turbo.
- [Voicci — Apple Silicon Whisper benchmarks](https://www.voicci.com/blog/apple-silicon-whisper-performance.html) — RTF table for M1/M2/M3/M4 on medium model.
- [Oliver Wehrens — RTX 4090 vs M1Pro/M2/M3 with MLX](https://owehrens.com/whisper-nvidia-rtx-4090-vs-m1pro-with-mlx/) — cross-platform context.
- [ggml-org/whisper.cpp GitHub](https://github.com/ggml-org/whisper.cpp) — CoreML encoder integration details.
- [mlx-whisper PyPI](https://pypi.org/project/mlx-whisper/) — install and CLI/Python usage.
- [ml-explore/mlx-examples whisper README](https://github.com/ml-explore/mlx-examples/blob/main/whisper/README.md) — official Apple reference.
- [mustafaaljadery/lightning-whisper-mlx GitHub](https://github.com/mustafaaljadery/lightning-whisper-mlx) — 4× mlx-whisper claim via batching.
- [huggingface/distil-whisper GitHub](https://github.com/huggingface/distil-whisper) — distil-large-v3.5 specs.
- [OpenAI whisper-large-v3-turbo HF card](https://huggingface.co/openai/whisper-large-v3-turbo) — 6× speedup, 4 decoder layers.
- [Calm-Whisper arXiv 2505.12969](https://arxiv.org/abs/2505.12969) — 80% non-speech hallucination reduction via 3-head fine-tune.
- [Investigation of Whisper hallucinations arXiv 2501.11378](https://arxiv.org/html/2501.11378v1) — VAD + BoH delooping as strongest baseline.
- [m-bain/whisperX GitHub](https://github.com/m-bain/whisperX) — VAD-first pipeline, pyannote integration, chunked long-form.
- [jianfch/stable-ts GitHub](https://github.com/jianfch/stable-ts) — `suppress_silence`, `nonspeech_skip`, `avg_prob_threshold` automatic hallucination filters.
- [snakers4/silero-vad GitHub](https://github.com/snakers4/silero-vad) — VAD library currently used by the agent; v5 caveats noted.
- [OpenAI discussion #679 — A possible solution to Whisper hallucination](https://github.com/openai/whisper/discussions/679) — community context for why non-speech trips Whisper.

---

**TL;DR for the main agent:** Yes, switch backends. Move from `faster-whisper (CPU, small/int8)` to `mlx-whisper` running `mlx-community/whisper-large-v3-turbo`. That one change gives roughly 4–6× speedup AND a meaningful accuracy upgrade (small → turbo is close to halving WER on English lectures) with ~30 minutes of work. Then layer `stable-ts` with `avg_prob_threshold=0.6` + `suppress_silence=True` on top for automatic in-stream hallucination suppression — this eliminates the need for the post-hoc delete+marker scanner script. If the 82-s silent-window hallucination still leaks through, swap Silero v5 for pyannote VAD (better silence-edge behavior). Do not adopt lightning-whisper-mlx yet — unmaintained re large-v3-turbo. Do not bother with Calm-Whisper unless residual hallucinations persist after the three main fixes. The full v2 upgrade (recs 1+2+3) should take 2–3 hours and make `transcribe.py` both dramatically faster and materially more robust.
