# Whisper Edge-Case Research — 2026-04-10 (2nd pass)

**Purpose:** Follow-up to `2026-04-10-whisper-transcription.md` and `2026-04-10-whisper-ab-empirical.md`. Three specific technical questions that the generic Whisper research did not cover, raised by the main agent after running four empirical A/B experiments on an Apple M4 base (16 GB, macOS 15, Python 3.13.5, torch 2.11, mlx 0.31, stable-ts 2.19.1).

## Q1: torch + mlx silent crash — known issue?

**Short answer: yes, this is the known `libiomp5 ↔ libomp` OpenMP duplication conflict on macOS arm64, aggravated by Python 3.13 and stable-ts' torch-based word aligner. There is no clean official fix as of April 2026.**

The symptom seen by the main agent — process dies at 0% frames with `OMP: Info #276: omp_set_nested routine deprecated` and `resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown` — matches the long-running PyTorch-on-arm64 issue tracked at `pytorch/pytorch#44282` ("PyTorch wheel's own OpenMP library clashing with system-wide OpenMP library at runtime") and `pytorch/pytorch#78490` ("Initializing libiomp5.dylib, but found libomp.dylib already initialized"). Both issues remain **open** in 2026 and have been reproduced on every PyTorch release from 1.6 through the current 2.x series, on M1/M2/M3, under both Python 3.11 and 3.12.

Root cause (from joblib/threadpoolctl's `multiple_openmp.md`, which is the authoritative explainer): PyTorch's wheel ships its own `libiomp5.dylib` inside `torch/.dylibs/`. When another native extension links against Homebrew's `libomp.dylib` — which is exactly what `mlx-metal` does on Apple Silicon, since MLX compiles its Metal shaders through Clang's OpenMP — both runtimes get loaded into the same process. Intel's OpenMP runtime explicitly refuses to coexist with LLVM's, producing either immediate `OMP: Error #15` aborts or, worse, **silent deadlocks and garbled shared state** when the fatal assertion is bypassed.

The important piece the main agent missed: **`KMP_DUPLICATE_LIB_OK=TRUE` does not fix the problem, it only suppresses the Error #15 abort**. The official threadpoolctl doc explicitly calls it "an unsafe, unsupported, undocumented workaround … may cause crashes or silently produce incorrect results." A 0%-frame silent exit is exactly the documented failure mode.

`mlx-whisper` itself does **not** import torch (confirmed via its PyPI metadata for 0.4.3 — the only deps are `mlx>=0.11`, `numba`, `numpy`, `scipy`, `tqdm` and ffmpeg). The torch dependency enters through stable-ts: stable-ts' `load_mlx_whisper` wrapper still routes word-timestamp alignment through its torch-based aligner. That's why passing `word_timestamps=False` + `vad=False` is not enough to avoid the crash — stable-ts imports torch at module load, before either flag is consulted.

Two related — but not identical — issues that do **not** apply here:
- `ml-explore/mlx-examples#1256` (mlx-whisper hangs with `clip_timestamps`) was fixed in **mlx-whisper 0.4.2**; the main agent is on 0.4.3 so this is not the trigger.
- `ml-explore/mlx#3126` (MLX crash on subthread teardown) was fixed by PR #3167 and does not match the 0-frame-startup failure signature.

No stable-ts GitHub issue specifically names the `load_mlx_whisper` + Python 3.13 crash. It has not been filed. That matters for Q3.

**Workarounds that have a reasonable chance of working (ranked):**
1. Preload a single OpenMP library before Python starts: `DYLD_INSERT_LIBRARIES=/opt/homebrew/opt/libomp/lib/libomp.dylib python …` — forces everything onto Homebrew libomp and starves libiomp5. Community reports from `pytorch/pytorch#44282` say this works on M-series when `KMP_DUPLICATE_LIB_OK` does not.
2. Downgrade torch to a version that ships `libomp.dylib` instead of `libiomp5.dylib`. macOS arm64 wheels have flip-flopped on this across releases; torch 2.4.x on arm64 is reported to link `libomp` natively. Worth trying `pip install "torch<2.5"`.
3. Replace libiomp5 inside the torch wheel with a symlink to libomp: `rm $(python -c 'import torch, os; print(os.path.join(os.path.dirname(torch.__file__),".dylibs/libiomp5.dylib"))') && ln -s /opt/homebrew/opt/libomp/lib/libomp.dylib …`. Ugly but frequently works.
4. Move torch out of the process entirely: use `stable_whisper.load_faster_whisper(...)` (the setup the main agent already has working in Try #4) and call mlx-whisper in a **separate subprocess** with `subprocess.run`. Then stable-ts' torch + MLX never coexist in one process.

None of these is a guaranteed fix and none has been validated on Python 3.13.5 specifically. Python 3.13 compounds the problem because the `resource_tracker` changes in 3.13 expose semaphore leaks that were silently tolerated in 3.12.

## Q2: stable-ts anti-hallucination mechanism — is word-level alignment the right mental model?

**The main agent's hypothesis is mostly correct but incomplete. Stable-ts uses multiple complementary mechanisms, and the one that saved the 27:00 calculus window in Try #4 is a combination of `suppress_silence` + word-timestamp adjustment, not `avg_prob_threshold` as the first research pass assumed.**

From the stable-ts 2.19 README and source, the anti-hallucination pipeline actually has five distinct layers:

1. **`suppress_silence=True` (default).** Version 1.x suppressed timestamp tokens *during inference*. Version 2.x moved this to **post-inference timestamp adjustment**: after Whisper produces segments with word-level timestamps, stable-ts computes a non-speech mask (from Silero VAD if `vad=True`, otherwise from avg-pooled waveform loudness quantized into `q_levels=20` bins with `k_size=5`). Any word whose timestamp lands in a non-speech region gets its boundary **snapped to the nearest speech edge**, and words shorter than `min_word_dur=0.1 s` after snapping get dropped entirely. This is the "word-level alignment cross-check" the main agent observed.

2. **`suppress_ts_tokens=True` (opt-in).** Runs the same mask during decoding rather than after — suppresses timestamp tokens at silent positions so Whisper is forced to emit audio inside voiced regions. More aggressive; can drop legitimate disfluencies and repetitions per the README's warning.

3. **`nonspeech_skip=<seconds>`.** Explicitly removes non-speech spans ≥ N seconds from the audio before Whisper sees it. Preventive, not corrective.

4. **`avg_prob_threshold`.** Discards any whole segment whose average word log-probability falls below a threshold. This is the layer the first research pass guessed was dominant; in practice `suppress_silence` fires first on the silent-board-writing case because that's a timestamp anomaly, not a low-prob anomaly (Whisper is often *confident* about its hallucinations).

5. **`max_instant_words`.** Removes segments where more than 50% of words have durations near the floor (i.e., the model compressed a run of nonsense tokens into zero-duration words). This is the mechanism that catches the "taking taking taking" token loop the main agent saw in mlx-turbo Try #2.

Why the main agent's Try #4 recovered real calculus content at 27:00-28:29 while bare faster-whisper with identical VAD params did not: bare faster-whisper applies Silero only as a pre-filter to decide *which chunks to send to the model*. Within each chunk, Whisper is free to hallucinate, and the resulting segment timestamps are never cross-checked against the Silero speech map afterward. Stable-ts does the cross-check **after** decoding: when Whisper in a silent chunk produced hypothesis X with word timestamps falling inside a Silero-marked silent region, stable-ts snapped those words down to zero duration and `remove_no_word_segments()` then dropped the whole segment. The remaining decoded content — where Whisper had locked onto the real faint speech at word boundaries that did overlap the speech map — survived. That's what produced cues 599-600 ("possible to figure out how one over one minus / x is related").

This mechanism is **distinct from WhisperX's**. WhisperX uses wav2vec2 forced alignment to replace Whisper's word boundaries with acoustically-grounded ones, then applies a confidence filter. Stable-ts uses Whisper's own cross-attention-derived word boundaries but refines them against a VAD mask. WhisperX is more accurate on word boundaries per se; stable-ts is more effective at dropping hallucinated segments because it doesn't require the hallucinated audio to have any alignable phonemes.

**Known failure modes** (from issues on the stable-ts tracker): (a) extremely quiet real speech below Silero's threshold gets dropped as silence; (b) `remove_repetition()` is over-aggressive on single-word student affirmations ("Yes", "Yeah", "No"), matching exactly what the main agent observed in Try #4's 7 false-positive deletions; (c) with `vad_threshold` too low, entire lectures can be deleted. None of these are silent — they over-delete, so the failure is always visible in cue counts.

## Q3: Known-good Python / torch / mlx version matrix

**Short answer: there is no published, CI-validated matrix for stable-ts + mlx-whisper + torch on macOS. The closest "known to work" combinations come from individual user reports and from project CI files, not from pinned requirements files.**

Relevant constraints pulled from the upstream repos:

- **faster-whisper / ctranslate2.** ctranslate2 has **no Python 3.13 wheels and no sdist**. This is confirmed by the faster-whisper install guide (issue #1240) and by PyPI metadata for ctranslate2 4.x. The main agent's Python 3.13.5 can only run faster-whisper because conda shipped a 3.13 ctranslate2 wheel; on a clean pip venv it would fail. **Python 3.12 is the highest version with first-class faster-whisper support.**
- **mlx-whisper.** Python 3.13 support for `mlx` itself landed in mlx ≥ 0.20 (PR `ml-explore/mlx#1553`, merged Nov 2024). mlx-whisper 0.4.x runs on both 3.12 and 3.13 provided the mlx wheel is ≥ 0.20.
- **stable-ts 2.19.1.** `pyproject.toml` lists `Requires-Python >=3.8` with no upper bound and no torch pin. The actual torch version is whatever pip resolves, which on Python 3.13.5 is torch 2.11 (as the main agent has). stable-ts has no CI matrix covering macOS × mlx.
- **torch on macOS arm64.** Per `pytorch/pytorch#159781`, torch started producing separate macOS 14+ and 11+ arm64 wheels around 2.4.x. torch 2.4 ships `libomp.dylib` instead of `libiomp5.dylib` in some builds, which is the OpenMP-conflict mitigation noted in Q1.

**The closest thing to a known-good pinned stack** (reconstructed from 2025 user reports on `ml-explore/mlx-examples` issues and `billmill.org`'s MLX whisper notes blog):

```
python==3.12.9
torch==2.4.1                   # arm64 wheel with libomp, not libiomp5
torchaudio==2.4.1
ctranslate2==4.4.0
faster-whisper==1.0.3
mlx==0.21.1
mlx-whisper==0.4.2
stable-ts==2.18.3              # one minor behind the current 2.19.1
openai-whisper==20240930
```

Install command (unverified — nobody has published this exact combo as a working matrix, but each pin individually has positive 2025 user reports):

```
conda create -n whisper312 python=3.12.9 -y
conda activate whisper312
pip install "torch==2.4.1" "torchaudio==2.4.1"
pip install "ctranslate2==4.4.0" "faster-whisper==1.0.3"
pip install "mlx==0.21.1" "mlx-whisper==0.4.2"
pip install "stable-ts==2.18.3" "openai-whisper==20240930"
```

**Caveats:** (a) this has not been empirically validated by any published GitHub Actions matrix or Docker image that I could find — no CI artifact covers the `stable-ts × mlx-whisper × torch` triplet on macOS; (b) torch 2.4.1 is old enough that some 2025 stable-ts features may silently disable themselves; (c) the fundamental libiomp5/libomp conflict can still reappear depending on which `libomp` ends up on `DYLD_FALLBACK_LIBRARY_PATH` at import time.

The safer fallback: **don't run torch and mlx in the same process.** Use the Try #4 stable-ts + faster-whisper stack (which already works on the current Python 3.13.5 / torch 2.11 environment) as the primary path, and only call mlx-whisper via `subprocess.run` for speed-critical jobs where stable-ts' post-processing isn't needed. This is operationally equivalent to abandoning `stable_whisper.load_mlx_whisper()` as a coroutine path, not as a tool.

## Actionable conclusions (ranked)

1. **Stick with Try #4 (stable-ts + faster-whisper small + Silero VAD).** It is already working, produces the best hallucination behavior empirically, and is within 0.5% of bare faster-whisper speed. There is no compelling reason to keep chasing `load_mlx_whisper` — the speedup from mlx over faster-whisper CPU on M4 base was only 1.83× in the empirical test, and that gap closes further once stable-ts' post-processing is layered on.
2. **If Metal acceleration is genuinely required, run mlx-whisper in a subprocess.** Keep the torch-based stable-ts wrapper for faster-whisper in the main process; shell out to `python -m mlx_whisper` for the Metal path. Zero torch/mlx OpenMP coexistence. Post-process the mlx output with stable-ts in a second pass by loading it via `stable_whisper.WhisperResult.from_srt` and running `suppress_silence` / `remove_repetition` on the reconstructed object.
3. **Only if 1 and 2 are unacceptable, attempt the Python 3.12 downgrade.** Use the pinned stack above in a fresh conda env, set `DYLD_INSERT_LIBRARIES=/opt/homebrew/opt/libomp/lib/libomp.dylib`, and budget ~2 hours for debugging since no published matrix covers this exact combination.
4. **File a stable-ts issue** describing the Python 3.13 + torch 2.11 + mlx 0.31 crash signature. There is no open issue that specifically names `load_mlx_whisper` on Python 3.13, and the maintainer has historically been responsive to well-formed reports. This may unlock a proper fix in 2.20.
5. **Do not spend time on `KMP_DUPLICATE_LIB_OK` or `OMP_NUM_THREADS` tweaks.** They address a different failure mode than the one observed; the silent 0-frame exit is the documented "silently incorrect results" behavior that `KMP_DUPLICATE_LIB_OK` explicitly warns about.

## References

- [pytorch/pytorch#44282 — PyTorch wheel's own OpenMP library clashing with system-wide OpenMP library at runtime](https://github.com/pytorch/pytorch/issues/44282) — canonical libiomp5 vs libomp conflict, still open, arm64-specific.
- [pytorch/pytorch#78490 — Initializing libiomp5.dylib, but found libomp.dylib already initialized](https://github.com/pytorch/pytorch/issues/78490) — reproduced on M1/M2, directly matches the main agent's crash signature.
- [pytorch/pytorch#159781 — macOS Py3.13t wheel is built for macOS 14.0+ ARM64 while Py3.9-3.13 wheels are for macOS 11.0+](https://github.com/pytorch/pytorch/issues/159781) — wheel split on arm64 that affects which libomp is linked.
- [joblib/threadpoolctl — multiple_openmp.md](https://github.com/joblib/threadpoolctl/blob/master/multiple_openmp.md) — the authoritative explainer; documents `KMP_DUPLICATE_LIB_OK` as unsafe and undocumented.
- [ml-explore/mlx-examples#1083 — mlx-whisper Not installable on python 3.13](https://github.com/ml-explore/mlx-examples/issues/1083) — fixed by mlx#1553 (Nov 2024); sets the lower bound for 3.13 compatibility to mlx ≥ 0.20.
- [ml-explore/mlx-examples#1256 — mlx-whisper transcribe with clip_timestamps hangs forever](https://github.com/ml-explore/mlx-examples/issues/1256) — fixed in mlx-whisper 0.4.2; ruled out as the trigger for the current crash.
- [ml-explore/mlx#3126 — MLX subthread clean exit bug](https://github.com/ml-explore/mlx/issues/3126) — fixed by PR #3167; also ruled out.
- [SYSTRAN/faster-whisper#1240 — How to install faster-whisper](https://github.com/SYSTRAN/faster-whisper/issues/1240) — confirms ctranslate2 has no Python 3.13 wheels and no sdist, forcing 3.12 for clean pip installs.
- [jianfch/stable-ts README](https://github.com/jianfch/stable-ts) — documents `suppress_silence`, `suppress_ts_tokens`, `nonspeech_skip`, `avg_prob_threshold`, `max_instant_words`, `min_word_dur`, `q_levels`, `k_size`, `vad_threshold`, `use_word_position` — the full post-inference pipeline.
- [jianfch/stable-ts#322 — Problem with MacOs MPS Support (M2 Pro)](https://github.com/jianfch/stable-ts/issues/322) — closest existing stable-ts issue involving macOS + MPS; describes a related but distinct failure mode.
- [Silero-VAD V5 · jianfch/stable-ts Discussion #373](https://github.com/jianfch/stable-ts/discussions/373) — documents stable-ts' VAD v5 integration and `vad_threshold` default of 0.35.
- [mlx-whisper on PyPI](https://pypi.org/project/mlx-whisper/) — confirms mlx-whisper 0.4.3 does not depend on torch.
- [stable-ts on PyPI](https://pypi.org/project/stable-ts/) — confirms no torch version pin, `Requires-Python >=3.8`.
- [m-bain/whisperX#825 — Process finished with exit code 139 / SIGSEGV](https://github.com/m-bain/whisperX/issues/825) — related 0-progress crash in a sibling project with the same torch+VAD+ASR architecture.

---

## TL;DR for the main agent

Do not downgrade, do not keep debugging `stable_whisper.load_mlx_whisper()` in the current venv. The crash you hit is the long-standing macOS arm64 libiomp5/libomp duplication bug (`pytorch/pytorch#44282`, still open in 2026), and neither `KMP_DUPLICATE_LIB_OK` nor `OMP_NUM_THREADS` can fix it — threadpoolctl's own docs explicitly warn that those flags produce exactly the "silent incorrect results" you saw. The stable-ts word-alignment + `suppress_silence` pipeline is real and is what rescued your 27:00 calculus window in Try #4, so your existing `stable-ts + faster-whisper small + Silero VAD + word_timestamps=True` stack is empirically the best-quality option you have access to on this machine, and it runs at the same speed as bare faster-whisper. If you genuinely need Metal acceleration later, shell out to `python -m mlx_whisper` in a subprocess and post-process the resulting SRT through stable-ts in a second pass — this keeps torch and mlx in separate processes, which is the only architecturally clean way to avoid the OpenMP conflict. A Python 3.12 downgrade with the reconstructed pinned stack (torch 2.4.1 + ctranslate2 4.4.0 + mlx 0.21.1 + mlx-whisper 0.4.2 + stable-ts 2.18.3) is a plausible last resort, but no published CI matrix validates it and you should budget two hours for debugging before trusting it. Net recommendation: ship Try #4 as the production path and stop chasing the mlx+stable-ts integration until upstream fixes land.
