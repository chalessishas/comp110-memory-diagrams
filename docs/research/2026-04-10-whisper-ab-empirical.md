# A/B Empirical Test — faster-whisper vs mlx-whisper on M4

**Date:** 2026-04-10
**Hardware:** Apple M4, 16 GB RAM, macOS Darwin 24.6.0
**Test audio:** `Review Session for Midterm 3.mp4` (87:28 min, 96 MB, English lecture)
**Follow-up to:** `2026-04-10-whisper-transcription.md` (the research report that recommended switching backend)

Before adopting the research report's recommendation, I ran the exact same 87-minute lecture through both stacks to measure the real improvement on **this specific machine and content**. Findings below both confirm and partially refute the report.

## Setup

| Field | A: faster-whisper (baseline) | B: mlx-whisper (research rec) |
|---|---|---|
| Library | `faster-whisper==1.2.1` | `mlx-whisper==0.4.3` + `mlx==0.31.1` |
| Runtime | CTranslate2 CPU (int8) | MLX Metal (GPU) |
| Model | `small` (~466 MB) | `mlx-community/whisper-large-v3-turbo` (~1.6 GB) |
| VAD | Silero v5 via faster-whisper's built-in | None (mlx-whisper has no VAD by default) |
| Anti-hallucination params | `condition_on_previous_text=False`, `compression_ratio_threshold=1.8`, `logprob_threshold=-0.8`, `no_speech_threshold=0.85` | Same four params |
| Script | `~/whisper-transcribe/transcribe.py` | `~/whisper-transcribe/transcribe_mlx.py` |

## Speed — mlx-whisper wins, but not by as much as the report claimed

| Metric | A | B | Ratio |
|---|---|---|---|
| Wall-clock time | **1288 s** (21:28) | **703 s** (11:43) | B is **1.83× faster** |
| Realtime factor | 0.245× | 0.134× | — |
| Audio/wall ratio | 4.08× realtime | 7.46× realtime | — |

The research report cited llimllib's Jan 2026 benchmark (mlx-whisper 2.03× faster than whisper.cpp on large-v3-turbo) and voicci's M-series tables showing 10–15× speed headroom. In practice on **M4 base + 16 GB**, I measured **1.83×** over faster-whisper CPU — real and meaningful, but nowhere near the 4–6× the report's recommendation block claimed.

### Why the gap?

Four factors, in order of contribution:
1. **I compared against a different baseline than the report.** The report's 2.03× figure is `mlx-whisper` vs `whisper.cpp` — *both* Metal-accelerated. My 1.83× is `mlx-whisper` vs `faster-whisper CPU` — different baselines.
2. **Model size inversion.** Baseline was `small` (~466 MB, ~244 M params). New was `large-v3-turbo` (~1.6 GB, ~809 M params). Turbo is 3.3× more parameters, so even with Metal acceleration the speedup over small's int8 is damped.
3. **Hardware is M4 base, not M2 Ultra.** Voicci's published numbers showing 0.08× RTF on `medium` were on M3/M4 Pro or Max. Base M4 has fewer GPU cores (10 vs 40 on Max).
4. **Observed thermal throttling.** The mlx run's frames/sec dropped from 1800 fps down to 200 fps several times during the 11-minute run (visible in the progress bar snapshots). Looks like the M4 fanless/passive cooling couldn't sustain peak GPU frequency.

**Corrected expectation for this hardware:** real-world speedup switching from `faster-whisper small/int8 CPU` to `mlx-whisper large-v3-turbo` on M4 base is **~1.8×**, not 4–6×. If you stay on the same model size (e.g. `mlx-whisper small`), the speedup would probably be ~3–4× because you'd also save the 3.3× param inflation. That's a parameter tuning experiment worth running next.

## Accuracy — mixed

Mlx-whisper large-v3-turbo produces **1114 segments** vs faster-whisper small's **1941**. Turbo groups utterances into longer chunks (avg ~4.7 s vs ~2.7 s), which is actually better for subtitle display — reads less like a live closed-caption feed, more like a clean transcript.

Spot-checking clean speech sections, both outputs convey the same meaning. Turbo's word-level accuracy feels slightly higher on harder words ("anti-derivative", "reverse power rule" — both models got these right in the A/B; the point is turbo didn't regress). **No obvious WER win in either direction on this clean English speech.** The report's claim that "small → turbo would cut WER roughly in half" did not manifest visibly — probably because `small` on English is already at 4–6% WER and turbo is 2–4%, which isn't a dramatic difference to a human reader.

## Hallucinations — **surprising result: turbo is WORSE, not better**

The research report claimed large-v3-turbo + strict params would reduce hallucinations. My empirical test contradicts this in a specific and interesting way.

### Hallucination count comparison

Ran `scan_hallucinations.py` (my 3-heuristic scanner) against both outputs:

| Heuristic | A (faster-whisper small) | B (mlx-whisper turbo) |
|---|---|---|
| 1. Long-duration + short-text filler | 18 matches (mostly legitimate — board writing) | **1 match** (cleaner) |
| 2. Same text repeated ≥3× consecutively | 0 | 1 ("Yes." ×3 — legitimate) |
| 3. Same phrase cumulative > 8 s | Two "opening up in any role" variants at 27:03-28:25 | **58.7 s of "taking taking taking ..."** spanning TWO locations |

### The "taking" loops in turbo

Turbo produced a **token-loop hallucination** — literally the word "taking" repeated ~150 times — in two places:

- **09:28 – 09:58** (30 s): a silent stretch where the instructor was waiting for a student to load a file. Baseline small said "One, one, one, one, one, one, one, one, one, one, one, one." — also garbage but shorter and not caught by my scanner's cumulative-duration heuristic. Turbo turned this into one giant 30-second cue of "taking taking taking".
- **27:00 – 28:29** (~89 s): the known hallucination window from the baseline run. Baseline small said "opening up in any role" / "sun and the rain" / "burns into the brain". Turbo said "taking taking taking" for 90 seconds.

**Both models hallucinate in the same audio locations** — the silent stretches. The difference is the *shape* of the hallucination:
- Small produces plausible-looking English sentences that sneak past shallow review.
- Turbo produces single-token loops that are glaringly obvious (and trivially detected by any scanner).

**This is actually a net positive for downstream processing**: token loops are easier to detect automatically than plausible sentences. But it means the research report's claim that "large-v3-turbo has better hallucination behavior" is not empirically true on this hardware + audio. The hallucinations just look different.

### What DID the anti-hallucination params accomplish?

I passed the same four strict params (`condition_on_previous_text=False`, `compression_ratio_threshold=1.8`, `logprob_threshold=-0.8`, `no_speech_threshold=0.85`) to both runs. The params prevented **cascade** hallucinations (where one bad segment contaminates the next) but did **not** prevent in-silence hallucinations. The root cause — Whisper trying to decode silence into text — is model-architectural, as Calm-Whisper's paper argues.

### Did `no_speech_threshold=0.85` work?

Arguably no. If it had been effective, turbo should have produced *empty* segments in 27:00-28:29, not 90 seconds of "taking". This suggests that raising `no_speech_threshold` alone isn't enough — the model assigns high speech probability even to silent stretches with classroom noise (chair scrapes, quiet chatter). **The right fix is an external VAD that drops the audio before it reaches Whisper** — either pyannote or Silero. Mlx-whisper's built-in pipeline has no VAD, which is why it's worse here despite having the same threshold.

## Empirical recommendations (revised from the research report)

The research report ranked `mlx-whisper + large-v3-turbo` as the "highest ROI" change. Based on this A/B:

1. **Backend switch IS worth it** — 1.83× speedup is real and the code is 40 lines. Effort: already done (30 min).
2. **But the research's speedup numbers were over-optimistic for M4 base.** Expect ~1.8× not 4–6× unless you also switch to a smaller model.
3. **The "turbo has better hallucination behavior" claim is empirically false on this hardware.** Turbo without a VAD prefilter is *worse* than small with Silero. Do NOT adopt turbo without adding a VAD.
4. **Most important unfinished step: add pyannote or Silero VAD BEFORE mlx-whisper decoding.** This is what WhisperX does and it's the single change most likely to eliminate hallucinations on this specific lecture.
5. **Test `mlx-whisper small` before going all-in on turbo.** I didn't test this. Same Metal acceleration but 3.3× fewer params should give ~3–4× speedup over faster-whisper small without the hallucination regression. **This is the experiment to run next.**
6. **Keep the post-hoc scanner script.** Even after all improvements, architectural hallucination means automatic detection is still valuable insurance. My existing `scan_hallucinations.py` would need a new heuristic: "single-word repetition >10 times in a single cue" — that would have caught the turbo "taking" loop.

## Artifacts

| File | Purpose |
|---|---|
| `~/whisper-transcribe/transcribe_mlx.py` | mlx-whisper version of the script |
| `~/Downloads/Review Session for Midterm 3.mlx.srt` | turbo output, 98 KB, 1114 cues |
| `~/Downloads/Review Session for Midterm 3.mlx.txt` | turbo plaintext, 60 KB |
| (preserved) `~/Downloads/Review Session for Midterm 3.srt` | faster-whisper output, cleaned, 123 KB, 1918 cues |
| (preserved) `~/Downloads/Review Session for Midterm 3.srt.bak` | faster-whisper raw, 125 KB, 1941 cues |

## TL;DR for future Whisper work (before the Try #3 update)

- Switching to mlx-whisper on Apple Silicon is worth it, but the **speedup is ~1.8× on M4 base, not 4-6×** as the research report claimed.
- **Large-v3-turbo hallucinates MORE than small** on this audio when neither has a proper VAD.
- The research report was right on direction, wrong on magnitude, and wrong on hallucination robustness. **Always A/B-test library benchmarks on your own hardware and content before trusting them.**

---

# Update: stable-ts experiments (Try #2–#4)

The research report's third core recommendation was `stable-ts` as the decoding wrapper with `avg_prob_threshold`, `suppress_silence`, and VAD filtering. I ran **three more experiments** to empirically test this.

## Summary of all four experiments

| # | Backend | Model | VAD | Post-processing | Wall time | Hallucinations |
|---|---|---|---|---|---|---|
| 1 | faster-whisper | small/int8 CPU | Silero v5 (built-in) | none | **1288 s** | 1 obvious window at 27:03-28:25, 1 mild at 09:28-09:58 |
| 2 | mlx-whisper | large-v3-turbo Metal | none | none | **703 s** | 2 "taking taking" token loops at 09:28 AND 27:00 — **worse** |
| 3a | stable-ts + mlx-whisper | large-v3-turbo Metal | stable-ts Silero | remove_repetition | **CRASHED at 0%** | — |
| 3b | stable-ts + mlx-whisper | large-v3-turbo Metal | none | remove_repetition + OMP env vars | **CRASHED at 0%** | — |
| 4 | **stable-ts + faster-whisper** | small/int8 CPU | stable-ts Silero | remove_repetition | **1295 s** | **Hallucinations ELIMINATED at 27:00, significantly improved at 09:28** |

## Try #3a and #3b: stable-ts + mlx-whisper crashed

Both `stable_whisper.load_mlx_whisper()` attempts died at 0% frames with the same signature:
```
Detected language: English
  0%|          | 0/524834 [00:00<?, ?frames/s]OMP: Info #276: omp_set_nested routine deprecated...
/opt/anaconda3/lib/python3.13/multiprocessing/resource_tracker.py:301: UserWarning: resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown
```

Exit code 0 both times, no SRT produced. Classic **OpenMP / PyTorch / mlx Metal threading conflict** on Python 3.13 + torch 2.11 + mlx 0.31. Setting `OMP_NUM_THREADS=1 KMP_DUPLICATE_LIB_OK=TRUE` did not help. Disabling `vad=True` also did not help — torch still loads for stable-ts' word-timestamp alignment, and that's enough to trigger the conflict.

**Verdict:** `stable-ts + mlx-whisper` is not a viable path on this software stack today. Would require either downgrading torch, pinning a different Python, or waiting for upstream to fix the thread model.

## Try #4: stable-ts + faster-whisper small — the winner

`stable_whisper.load_faster_whisper("small", device="cpu", compute_type="int8")` with:
- `vad=True` (stable-ts Silero pre-filter)
- `word_timestamps=True`
- `suppress_silence=True`
- Same four anti-hallucination params as all previous runs
- Post-processing: `result.remove_repetition()` + `result.remove_no_word_segments()`

### Speed

**1295.2 s** — within 0.5% of the bare faster-whisper baseline (1288 s). The extra stable-ts layer adds ~7 seconds of overhead on an 87-minute lecture, negligible.

### Hallucination scan (all three heuristics)

| Heuristic | Baseline fw-small | mlx-turbo | stable-ts + fw-small |
|---|---|---|---|
| 1. Long-seg + short-text (filler) | 18 | 1 | **1** |
| 2. ≥3× consecutive repeats | 0 | 1 (legit "Yes.") | **0** |
| 3. Same phrase cumulative >8 s | 2 ("opening up in any role" variants) | 1 ("taking taking taking") | **0** |

Scanner shows **zero detectable hallucinations** in the stable-ts output. This is strictly better than both Try #1 (2 flagged phrases) and Try #2 (58.7 s of "taking" loop).

### 27:00-28:25 window — real content recovered

This is the headline result. The 82-second silent stretch where the instructor was at the board:

**Baseline fw-small (cleaned to marker in Turn 68):**
> "There, can you see it's opening up in any role?"
> "Yeah, but it's not opening up in any role." ×4
> "You're in no way to do that."
> "You sort of need to be in space."
> "But we're going to give you an example you can trust."
> "So where is the center for my?"
> "You know, it burns into the brain."
> "going to be more comfortable in the city, right?"
> "it's going to be just the sun and the rain."
> "Order and grade."

**mlx-whisper turbo:**
> "taking taking taking taking taking taking ..." (×150)

**stable-ts + fw-small (Try #4):**
> cue 593: "Can you go for this 6.22?"
> cue 594: "Yes." (7 s — probably a quiet student response padded by VAD)
> cue 595: "We are going to give you an example of what you're"
> cue 596: "going to end up doing to give me"
> cue 597: "Yeah,"
> cue 598: "and my question is about whether it's"
> cue 599: **"possible to figure out how one over one minus"**
> cue 600: **"x is related."**
> cue 601: "I would just take the derivative or not take the derivative,"
> cue 602: "but I would first figure"

Cues 599-600 are **actual calculus content** — the instructor is previewing that she'll work `1/(3+x)²` by relating it to `1/(1-x)`, which is exactly what she does at 28:30. The stable-ts pipeline **recovered real speech that the bare faster-whisper pipeline failed to transcribe**.

### Why did stable-ts recover real content?

Both baseline and Try #4 use Silero VAD. The difference is in HOW VAD gets consulted:

- **Baseline faster-whisper**: Silero runs pre-inference, returns speech regions, and Whisper decodes inside those regions with no further cross-checking.
- **stable-ts**: Silero also runs pre-inference, but stable-ts additionally (a) uses **word-level timestamps** to align audio to text and (b) uses that alignment to **reject segments whose word boundaries don't match the VAD speech map**. Segments where Whisper's hypothesis drifts into a VAD-marked silent region get trimmed or dropped automatically.

This word-level cross-check is what caught the hallucinations. It's more subtle than what the research report described (`avg_prob_threshold=0.6`) but accomplishes the same goal: in-stream rejection of segments whose confidence/grounding is low.

### 09:28-09:58 window (the other hallucination site) — also improved

**Baseline**: "One, one, one, one, one, one, one, one, one, one, one, one." (stuck-loop)
**mlx-turbo**: "taking taking taking..." (30 s token loop)
**stable-ts + fw-small**:
> "Honestly, let's use this as a complicated element that we"
> "would want to involve to the one line of x squared."
> "Can you just do the calculation that is"
> "that value of the series of plus one,"

Still wrong phonetically ("one line of x squared" is mishearing of "one over one minus x squared") but **no token loops, and the real content structure — "power series" / "calculation" / "value of series" — is captured**. A significant improvement, not perfect.

### False positives from remove_repetition()

Of the 11 items `remove_repetition()` removed:
- 7 were single-word student responses ("Yes.", "Yeah.", "No.", "What", "let's") — **probable false positives** (real content)
- 4 were likely filler words

The net effect is mild over-aggression. `remove_repetition()` is useful but should probably be called with stricter settings (`max_words=2` or higher) to avoid removing single legitimate short responses. Not a blocker.

## Final recommendations (replacing the initial v2 plan)

1. **For Apple Silicon Whisper on English lectures: use `stable_whisper.load_faster_whisper("small", compute_type="int8")` with `vad=True, word_timestamps=True, suppress_silence=True`** plus the four anti-hallucination params. This produces output strictly better than bare faster-whisper at the same speed.

2. **Do NOT use `stable_whisper.load_mlx_whisper()`** on Python 3.13 + macOS 14 today. The torch/mlx threading conflict silently kills the process. Revisit when torch 2.12+ lands or stable-ts adds a native MLX wrapper that doesn't import torch.

3. **Do NOT use bare `mlx-whisper large-v3-turbo` alone.** On this hardware + content it's faster but produces more hallucinations. If you want Metal acceleration, pair it with an external VAD layer — but then you lose the stable-ts word-level cross-check, so the net may be worse than plain stable-ts + faster-whisper.

4. **Keep the post-hoc `scan_hallucinations.py` scanner** as a second line of defense. Even stable-ts' best-case output can have residual drift ("one line of x squared"), and the scanner is cheap insurance.

5. **Tune `remove_repetition()` for English lectures**: use stricter min-repeat settings to avoid deleting legitimate short student responses. Or skip `remove_repetition` entirely if the scanner shows no token-loop hallucinations.

## TL;DR (final)

- **Winner: stable-ts + faster-whisper small + Silero VAD + word timestamps.**
- Same speed as bare faster-whisper (21 min for 87-min lecture), zero detectable hallucinations, and actually recovered real calculus content from the silent board-writing stretch that all other configurations mangled.
- The research report's magnitude estimates were wrong (mlx-whisper is only 1.83× faster on M4 base, not 4-6×) and its model choice was wrong (turbo hallucinates more than small on quiet classroom audio), but its core insight — **stable-ts as a wrapper fixes hallucinations** — turned out to be correct, just via a different mechanism than the report described.
- The whole four-experiment matrix took about 90 minutes of wall-clock time. ROI is strong **only if more Whisper transcription jobs are coming**; for a one-off task the Turn 68 cleaned SRT was already sufficient.
