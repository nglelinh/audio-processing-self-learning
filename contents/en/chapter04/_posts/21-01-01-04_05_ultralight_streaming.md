---
layout: post
title: "04-05 Ultra-light streaming models"
chapter: "04"
order: 5
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

Not every product needs DeepFilterNet3-class capacity. **Ultra-light** streaming SE models target tens of MMACs and tiny memory for DSPs, hearables, and low-end phones. This survey lesson teaches the selection criteria—especially **MAC count ≠ wall-clock RTF**—and names well-known pointers: **GTCRN**, **FastEnhancer**, **μNet**, **Fast-ULCNet** (and related ULCNet line). Use them as a shortlist vocabulary, not as mandatory rewrites.

## Learning objectives

You will explain why operator choice and memory traffic dominate RTF, name the survey models above with one-line roles, list shortlisting criteria for on-device NS, and decide when to prefer DF3-quality vs ultra-light.

## 60-minute teaching plan

- **0–10 min** — Product scenarios: hearable vs laptop browser tab.
- **10–25 min** — MACs vs RTF vs memory; CPU-friendly ops.
- **25–40 min** — Pointer tour: GTCRN, FastEnhancer, μNet, Fast-ULCNet.
- **40–50 min** — Streaming state drift issues (high level).
- **50–60 min** — Decision checklist; exercises.

## Core explanation

### The industrial theme

Ultra-light SE papers optimize for:

- **Params** (tens to hundreds of KB),
- **MACs / frame**,
- **Causal latency** (often one hop),
- **Embedded benchmarks** (Cortex-A, HiFi DSP, Raspberry Pi, phone CPUs).

They may lose to DF3 on rich full-band quality—but win when the alternative is “NS off.”

### MAC count ≠ wall-clock RTF

FastEnhancer-style work emphasizes that **complex grouped / subband operators** can look cheap in MAC tables yet run slowly on CPUs because of gather/scatter, poor cache locality, and unfriendly kernels in ONNX Runtime. Conversely, a slightly higher MAC **plain** encoder–decoder + fused GEMM can win RTF.

**Measurement rule (Ch. 05):** report single-thread RTF on the target device with warm cache **and** under audio-callback pacing—not only paper MACs.

### Survey pointers (one line each)

| Model | One-line role |
|-------|----------------|
| **GTCRN** | Ultra-light grouped CRN baseline widely cited for tiny SE |
| **FastEnhancer** | Speed-oriented streaming SE; ONNX RTF mindset |
| **μNet** | Extreme low-memory DSP / hearable profile |
| **Fast-ULCNet** | ULCNet successor themes; notes long-stream RNN state issues |
| **ULCNet** (family) | Lightweight full-band SE / hybrid AENR companion |

Related names you may see in the same cluster: UL-UNAS, AdaptCRN, CoFi-Lite, FSPEN—optional deeper reading; not required for exams.

### Streaming state drift (preview of 05-04)

Tiny RNNs running for hours can **drift**: hidden states wander, causing gradual quality loss or pumping. Fast-ULCNet literature discusses state drift and complementary-filter style mitigations at a high level. Product mitigations:

- Periodic soft state reset during detected silence,
- Bounded state norms,
- Test **30+ minute** streams, not 3-second clips.

### When to prefer DF3 vs ultra-light

Prefer **DF3-class** when:

- Target is desktop/laptop browsers with WASM SIMD,
- Quality / full-band clarity is the differentiator,
- Model download size of a few MB is acceptable (Ch. 06 packaging).

Prefer **ultra-light** when:

- DSP / hearable / very low-end mobile CPU,
- Hard real-time ≤ few ms algorithmic latency,
- Memory budget ≪ DF3,
- You can accept more residual noise.

**Hybrid option:** classical AEC + ultra-light residual NS on embedded; DF3 in desktop Electron/web.

## Shortlist criteria checklist

1. Causal? Look-ahead frames?
2. Sample rate (16 vs 48 kHz)?
3. Measured RTF on **your** device class (ORT/WASM).
4. Model size + cold-start load time.
5. Long-stream stability test plan.
6. License and patent posture of weights/code.
7. ONNX op coverage in your runtime.

## Pitfalls

- Choosing a model from a MAC table alone.
- Porting grouped convolutions without SIMD kernels.
- Skipping long-stream tests.
- Mixing 16 kHz ultra-light weights into a 48 kHz pipeline without resampling policy.

## Exercises

1. **Scenario pick.** For (a) AirPods-class DSP, (b) mid laptop Chrome, (c) Raspberry Pi speakerphone—pick DF3 vs ultra-light and justify in 5 bullets each.
2. **RTF plan.** Write a measurement harness outline: warm-up frames, p50/p95 RTF, thread affinity notes.
3. **State drift.** Propose an experiment to detect gradual degradation over 45 minutes.
4. **Reading.** Open FastEnhancer and GTCRN abstracts; extract claimed latency and compute class only (no fabricated numbers beyond the abstracts).

## Further reading

- GTCRN (ICASSP ultra-light CRN line).
- FastEnhancer paper / code (ONNX Runtime RTF focus).
- μNet, Fast-ULCNet / ULCNet papers (ultra-light / embedded SE).
- DeepFilterNet2/3 — quality-side comparison baseline.
