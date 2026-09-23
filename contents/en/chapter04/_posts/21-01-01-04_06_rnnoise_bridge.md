---
layout: post
title: "04-06 RNNoise as a teaching bridge"
chapter: "04"
order: 6
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

**RNNoise** remains one of the best teaching artifacts in real-time NS: a **classical DSP front-end** (pitch-aware band features) plus a **small GRU** that predicts band gains, shipped as portable C with clear latency behavior. It will not match DeepFilterNet3 on full-band perceptual quality, but it teaches hybrid design, gain smoothing, and embedded deployment habits that transfer to WASM ports and ultra-light models.

## Learning objectives

You will summarize RNNoise’s hybrid philosophy, contrast its feature/gain pipeline with DeepFilterNet’s ERB+deep-filter approach, extract reusable lessons for WASM/embedded inference, and list limits that motivate DF-class models in Mezon.

## 60-minute teaching plan

- **0–10 min** — Listen: RNNoise vs modern full-band NS narrative.
- **10–25 min** — Pitch / bark-like bands / gain prediction architecture cartoon.
- **25–40 min** — Why the C implementation is a gift for systems engineers.
- **40–50 min** — Transferable lessons vs DF3 product path.
- **50–60 min** — Exercises; when to keep RNNoise in the lab.

## Core explanation

### Hybrid philosophy

RNNoise does **not** feed raw STFT bins into a huge net. It:

1. Computes **hand-designed features** (band energies, pitch-related cues),
2. Runs a **compact neural net** (GRU stacks) to predict **per-band gains**,
3. Applies gains with DSP smoothing / pitch heuristics to reduce artifacts.

That is the spiritual predecessor of “ERB gains + learned refinement,” with a much smaller compute envelope and historically telephony-oriented bandwidth.

### Operational complexity mindset

| Topic | RNNoise mindset | DeepFilterNet mindset |
|-------|-----------------|------------------------|
| Features | DSP pitch + bands | Learned ERB + STFT deep filter |
| Net size | Tiny GRU | Larger causal net |
| Bandwidth | Classic wideband telephony roots | Full-band 48 kHz target |
| Code | Self-contained C | Rust/Python training + exported graphs |
| Teaching value | Systems + hybrid clarity | Modern quality baseline |

### Why RNNoise is a great lab companion

- Students can read the C sources end-to-end in a sitting.
- Easy to instrument: log gains, plot band SNRs.
- Natural gate to **SIMD**, fixed-point thinking, and callback-friendly `process_frame` APIs (Ch. 05–06).
- Sets emotional expectations: **small models can work** if features are good.

### Limits (honest)

- Full-band music-like noise and modern laptop café scenes often need stronger models.
- Hand features can miss cues that deep complex filters capture.
- Quality ceiling below DF2/DF3 on many DNS-style full-band tests (verify with your own listening—don’t invent numbers).

**Mezon posture:** ship DF3-class for product quality; keep RNNoise (or SpeexDSP) as a **lab baseline** and regression oracle (“does our pipeline still beat classical?”).

### Reusable lessons for WASM / embedded

1. **Frame-native API** — process exactly one hop per call; no hidden heap churn.
2. **Precompute tables** — window, filterbanks.
3. **Smooth gains** — avoid musical noise (Ch. 03).
4. **Compile with SIMD** when available (Ch. 06).
5. **Hybrid humility** — classical features still help tiny nets.

## Pitfalls

- Dismissing RNNoise as “obsolete” and skipping its systems lessons.
- Expecting RNNoise defaults to match DF3 MOS.
- Porting only the GRU and dropping pitch/DSP logic.
- Using RNNoise as the only baseline in a full-band 48 kHz product evaluation.

## Exercises

1. **Architecture card.** Draw RNNoise’s feature → GRU → band gain → synthesis chain; annotate approximate frame size from the official repo docs.
2. **A/B lab.** Run RNNoise and a DF3 demo on the same clip; write a 10-line listening report (noise, speech distortion, musical artifacts).
3. **API design.** Sketch a Rust or C API `process_frame(&mut state, in, out)` inspired by RNNoise for a DF-lite student project.
4. **Hybrid proposal.** Invent (on paper) one classical feature you might add before a tiny GTCRN-class net for keyboard-click noise.

## Further reading

- RNNoise paper and official Xiph / JM Valin repository.
- SpeexDSP preprocessor — classical companion baseline.
- DeepFilterNet intro paper — contrast reading.
- WebRTC APM NS — another production classical/hybrid reference.
