---
layout: post
title: "01-07 Fourier pitfalls checklist for engineers"
chapter: "01"
order: 7
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

When NS “sounds broken,” engineers often retrain models first. This lesson is a pre-flight Fourier/STFT checklist: units, windows, symmetry, scaling, resampling, and DC/Nyquist — so you blame the network last.

## Learning objectives

1. Diagnose common FT/DFT mistakes in audio pipelines.
2. Validate units (Hz vs bin vs normalized frequency).
3. Apply a structured pre-flight checklist before blaming the neural model.
4. Recognize window/COLA and conjugate-symmetry failures by ear and by test.
5. Tie checklist items to Mezon / DeepFilterNet-style debugging without inventing internals.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–8 | War story format: symptom → wrong root cause → actual bug |
| 8–30 | Walk the master checklist with demos/thought experiments |
| 30–45 | Unit tests you should keep in repo |
| 45–55 | Mezon/DeepFilterNet debugging order |
| 55–60 | Exercises |

## Core explanations — master checklist

### 1) Sample rate truth

- [ ] PCM rate equals model rate (or documented resampler in between).
- [ ] Anti-alias filter present on downsampling.
- [ ] `AudioContext.sampleRate` not assumed 48 kHz on all devices.

**Symptom of failure:** robotic pitch shifts, dull audio, mysterious noise textures.

### 2) Units on the frequency axis

- [ ] Bin \(k\) converted with \(f=k f_s/N\).
- [ ] Filters specified in Hz converted using actual \(f_s\).
- [ ] Plots labeled Hz, not raw bin indices, in QA reports.

### 3) FFT normalization / Parseval

- [ ] Forward/inverse scaling matches library docs.
- [ ] Round-trip STFT→ISTFT on impulse/random noise preserves energy (±window gain).
- [ ] Training and inference use the same norm.

**Symptom:** output gain pumping; metrics disagree with listening.

### 4) Window & COLA

- [ ] Analysis window documented.
- [ ] Synthesis window + hop satisfy COLA (constant overlap-add) for perfect reconstruction when \(\hat{X}=X\).
- [ ] Same windows as training for neural front-ends.

**Symptom:** amplitude modulation at hop rate (tremolo), metallic warble.

### 5) Conjugate symmetry / packing

- [ ] Real iFFT inputs Hermitian.
- [ ] Nyquist/DC imaginary parts ~0.
- [ ] Packed real-FFT formats decoded correctly.

**Symptom:** imag leftovers, subtle distortion, framework errors.

### 6) Channel layout

- [ ] Interleaved vs planar agreed.
- [ ] Stereo → mono policy (mean / left / HRIR — pick one).
- [ ] Output channels match sink expectations.

### 7) Hop / latency accounting

- [ ] Look-ahead documented in ms.
- [ ] Ring buffer latency included in UX budget.
- [ ] Warmup frames discarded consistently in metrics.

### 8) DC and low-frequency junk

- [ ] DC blocker / high-pass if mic bias present.
- [ ] Not confusing DC with “noise” the model should remove.

### 9) dB displays

- [ ] \(20\log_{10}|X|\) vs \(10\log_{10}|X|^2\) consistency.
- [ ] Floor clamps to avoid \(\log 0\).

### 10) Resampler + model domain

- [ ] Eval metrics at agreed rate.
- [ ] No double resampling in A/B tools.

## Worked debugging scenarios

### Warble at 100 Hz

Hop 10 ms → 100 hops/s. If COLA broken, amplitude modulates near 100 Hz. Fix windows/hop before touching weights.

### “Model muted fricatives”

Confirm input actually has energy >6 kHz (rate might be 8 kHz). Confirm mask not low-passing due to wrong bin mapping at 48 vs 16 kHz.

### SI-SDR great, users hate it

Phase/complex issues or musical noise; check symmetry and time-domain artifacts; run listening (Ch. 08).

## Unit tests to keep

1. Impulse round-trip STFT/ISTFT (COLA).
2. Parseval check on FFT wrapper.
3. Hermitian projection test after random mask (optional).
4. Resampler sine: 1 kHz in → 1 kHz out, no alias spur.
5. Mono downmix length/channel asserts.

## Mezon / DeepFilterNet debugging order (public)

1. Verify PCM rate/channels against package README / model card.
2. Verify frame delivery (callbacks, ring buffer) — Ch. 05 themes.
3. Verify STFT hygiene (this checklist).
4. Only then swap model variants / strengths / npm options.
5. Cite public DeepFilterNet papers for expected algorithmic behavior; do not claim unpublished Mezon graph details.

## Common pitfalls

1. Changing three things at once (rate, hop, model).
2. Trusting a single café demo.
3. Using offline non-causal checkpoint in a streaming wrapper accidentally.
4. Ignoring p99 hop times.
5. “Fixing” warble with more aggressive NS gain.

## Mini exercises

1. Pick three checklist items and write a unit test name for each.
2. Hop 5 ms warble frequency if COLA fails?
3. Why does wrong \(f_s\) in \(f=kf_s/N\) mimic a bad model?
4. Draft a 6-step incident report template for “NS sounds bad in Chrome.”
5. Which checklist item catches interleaved stereo fed to a mono FFT?

## Further reading

- Oppenheim & Schafer — windows, scaling, DFT pitfalls chapters.
- DeepFilterNet papers — configuration & real-time notes.
- ORT / browser profiling docs (high level) for separating STFT vs net costs.
