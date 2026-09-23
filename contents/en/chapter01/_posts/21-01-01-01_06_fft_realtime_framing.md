---
layout: post
title: "01-06 FFT in real-time framed audio"
chapter: "01"
order: 6
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

An FFT textbook ends at complexity; a product starts at the callback. This lesson places FFTs inside streaming STFT frames: hops per second, algorithmic latency, buffer reuse, and a DeepFilterNet-oriented case study pointer.

## Learning objectives

1. Budget FFT cost inside a frame callback / AudioWorklet quantum.
2. Relate hop size, \(N\)-point FFT, and algorithmic latency.
3. Compute FFTs/s for common speech configurations.
4. Identify when FFT dominates RTF versus neural ops.
5. Apply streaming hygiene: preallocated buffers, plan reuse, OLA continuity.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Streaming STFT as repeated windowed FFTs |
| 10–25 | Numerics: hops/s, FFTs/s, latency formulas |
| 25–40 | Audio thread constraints; ring buffers; underrun math |
| 40–52 | Case study pointer: DeepFilterNet STFT configuration |
| 52–60 | Exercises |

## Core explanations

### Streaming STFT loop

Each hop:

1. Assemble \(L\) samples (from ring buffer) with hop advance \(R\).
2. Multiply by analysis window \(w\).
3. FFT → \(X(\ell,\cdot)\).
4. Enhance → \(\hat{X}(\ell,\cdot)\) (mask/filter/net).
5. iFFT → windowed frame; overlap-add into output ring.

State across hops: OLA buffer, any RNN/DF state, noise tracker state.

### Key formulas

$$
T_{\mathrm{hop}}=\frac{R}{f_s},\qquad
\mathrm{hops/s}=\frac{f_s}{R}
$$

With analysis FFT and synthesis iFFT each hop (typical):

$$
\mathrm{FFTs/s}\approx 2\cdot\frac{f_s}{R}
$$

(per channel). Stereo without downmix doubles that.

**Algorithmic buffering** is at least related to \(L\) and look-ahead frames; details in Ch. 02. Rule of thumb: larger \(L\) → better frequency detail, more delay.

### AudioWorklet quanta vs STFT hops

Browser render quanta are often 128 samples. At 48 kHz, \(128/48000\approx2.67\,\mathrm{ms}\). Your STFT hop might be 5–10 ms. Design a ring buffer: accumulate quanta until a hop is ready; never assume quantum == hop.

### Underrun inequality

Let \(T_{\mathrm{proc}}(\ell)\) be wall time for hop \(\ell\). Need

$$
T_{\mathrm{proc}}(\ell) < T_{\mathrm{hop}}
$$

almost always, with cushion for jitter. If neural net averages 3 ms but spikes to 12 ms on a 10 ms hop, you glitch.

### DeepFilterNet-oriented case study (public papers)

DeepFilterNet family papers describe STFT-based front-ends with ERB-scale features and deep filtering on complex spectra, engineered for **real-time** operation. When you read them (Ch. 04), extract: sample rate, window/FFT size, hop, and causal claims. Map those numbers onto the formulas above before integrating `deepfilternet3-noise-filter` or custom ORT graphs. Do not invent undocumented Mezon-specific STFT constants — read the package/model docs you actually ship.

### Implementation hygiene checklist

| Do | Don’t |
|----|-------|
| Preallocate hop scratch, FFT workspace | `malloc` / JS `new Float32Array` per hop on audio thread |
| Reuse FFT plans | Rebuild plans each callback |
| Fixed mono policy | Silently ignore second channel |
| Measure p95/p99 hop time | Trust mean RTF only |

## Worked examples

### FFTs per second

\(f_s=48\,\mathrm{kHz}\), \(R=480\) (10 ms): hops/s=100, FFT+iFFT ≈200 transforms/s/channel.

\(f_s=16\,\mathrm{kHz}\), \(R=160\) (10 ms): same 100 hops/s; smaller \(N\) often.

### Latency sketch

\(L=20\,\mathrm{ms}\), \(R=10\,\mathrm{ms}\), model look-ahead 1 hop → ballpark algorithmic delay tens of ms (exact depends on OLA definition). Product budgets must measure end-to-end.

### When FFT dominates

Classical spectral subtraction on MCU: FFT~all. DFN-class on laptop: net~all. Mobile mid-tier + debug WASM without SIMD: both hurt — profile.

## Common pitfalls

1. Equating AudioWorklet quantum with model hop.
2. Measuring latency with wall clock only on the main thread.
3. Resetting OLA state every callback.
4. Running stereo FFTs when model is mono.
5. Forgetting that iFFT + OLA is part of the budget, not “free after the net.”

## Mini exercises

1. \(f_s=16\,\mathrm{kHz}\), \(R=256\): hop ms and hops/s?
2. Budget \(T_{\mathrm{proc}}\) for RTF 0.4 at that hop.
3. 128-sample quantum at 48 kHz: how many quanta to fill a 10 ms hop?
4. List state that must persist across hops for STFT-NS.
5. Sketch a profiler plan separating STFT vs neural vs ISTFT time.

## Further reading

- DeepFilterNet / DeepFilterNet2 / DeepFilterNet3 papers — STFT / real-time configuration sections.
- MDN AudioWorkletProcessor documentation.
- WebRTC APM overview (processing in framed blocks).
