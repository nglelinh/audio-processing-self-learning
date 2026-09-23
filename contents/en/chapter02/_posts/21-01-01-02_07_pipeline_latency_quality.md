---
layout: post
title: "02-07 Pipeline latency–quality tradeoffs"
chapter: "02"
order: 7
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Every STFT and model choice is a deal with latency, CPU, and quality. This lesson closes Chapter 02 by making those tradeoffs explicit for real-time Mezon-aligned pipelines.

## Learning objectives

1. Enumerate pipeline stages that add latency and CPU.
2. Trade window/hop/FFT size against quality and delay with numbers.
3. Explain quality failure modes when over-optimizing latency.
4. Build a go/no-go scorecard for shipping configurations.
5. Connect tradeoffs to DeepFilterNet-class real-time design goals.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | End-to-end pipeline diagram (mic → NS → encoder) |
| 10–28 | Parameter sweep thought experiments with numerics |
| 28–42 | Quality vs latency failure modes |
| 42–52 | Scorecard for Mezon-like shipping |
| 52–60 | Exercises |

## Core explanations

### Pipeline stages (typical)

1. Capture / AudioWorklet quantum buffering
2. Resample to model rate
3. Mono downmix
4. STFT framing (window/hop)
5. Feature transform (e.g. ERB)
6. Neural / classical enhance
7. Inverse features / ISTFT / OLA
8. Resample to sink rate
9. Hand off to WebRTC encoder

Each stage: measure ms and RTF contribution.

### Knobs and effects

| Knob ↑ | Latency | CPU | Quality tendency |
|--------|---------|-----|------------------|
| Window \(L\) | ↑ | ↑ (larger FFT) | better freq detail; blurrier time |
| Hop \(R\) | ↓ if smaller? (more CPU) — smaller hop ↓ granularity delay sometimes but ↑ CPU | ↑ as \(R\)↓ | smoother masks often |
| Model size | ≈ (if lookahead fixed) | ↑ | often ↑ until RTF fails |
| Look-ahead | ↑ | ↑ | often ↑ quality |
| Sample rate | ↑ | ↑ | ↑ bandwidth if model trained for it |

Exact arrows depend on implementation; **measure**.

### Numerics to keep

At 48 kHz:

- 128-sample quantum ≈ 2.67 ms
- 480-sample hop = 10 ms → 100 decisions/s
- 960-sample window = 20 ms buffering scale

At 16 kHz, same *ms* windows use fewer samples (cheaper FFTs) but less bandwidth.

### Failure modes

**Too little latency budget:** tiny windows → pitch harmonics unresolved → harsh masks; or model too small → under-suppression.

**Too much latency:** conversational awkwardness; AEC alignment issues if NS sits wrong in the graph.

**Too little CPU headroom:** p99 glitches users hear as “NS crackles.”

### Shipping scorecard (example)

| Criterion | Target (illustrative) | Pass? |
|-----------|----------------------|-------|
| Algorithmic look-ahead | ≤ product budget (e.g. 20–40 ms class) | |
| p95 RTF on device | ≤ 0.5 | |
| COLA round-trip | error below threshold | |
| DNSMOS / listening | vs baseline WebRTC NS | |
| No hop warble | listening + spectrogram | |

Replace illustrative numbers with your product’s SLA.

### DeepFilterNet-class moral

Papers emphasize real-time operation: architectures and STFT settings are chosen to keep causal delay and compute practical. When integrating public Mezon packages, treat published model constraints as hard requirements; tradeoffs happen around **graph placement, resampling, and device budget**, not silent changes to pretrained STFT sizes.

## Worked examples

### Sweep

Config A: 16 kHz, L=20 ms, R=10 ms, small model, RTF 0.2, MOS OK.
Config B: 48 kHz, L=40 ms, R=5 ms, large model, RTF 0.9, MOS higher offline, glitches on phone → **do not ship B**.

### Budget split

40 ms total algorithmic budget: 20 ms window, 10 ms hop look-ahead, 10 ms misc buffering — if model needs 30 ms look-ahead, renegotiate product or model.

## Common pitfalls

1. Optimizing mean RTF only.
2. Changing L/R without regenerating eval sets.
3. Comparing quality at different latencies unfairly.
4. Ignoring resample cost in RTF.
5. Shipping debug builds’ timings as production truth.

## Mini exercises

1. Draw the 9-stage pipeline and mark where you would log timestamps.
2. If hop goes 10→5 ms, what happens to hops/s and CPU roughly?
3. Propose three scorecard metrics for a customer-support softphone.
4. Why might 48 kHz hurt a 16 kHz-trained model even if CPU allows?
5. Name one quality artifact from too-short windows.

## Further reading

- DeepFilterNet2/3 real-time design sections.
- WebRTC APM latency considerations (docs).
- MDN AudioWorklet performance guidance.
