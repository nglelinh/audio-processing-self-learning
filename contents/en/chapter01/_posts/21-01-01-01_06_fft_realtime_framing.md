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

![Overlapping analysis frames, each one a windowed FFT, added back on the synthesis side]({{ site.imgurl }}/generated/stft-ola.png)

*Figure. Real-time FFT work is this picture on a clock: one new hop in, one windowed transform, overlap-add out. The basis is still the DFT basis; the schedule is the hop.*

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

**One configuration, fully counted.** Take \(f_s=48\,\mathrm{kHz}\) (the full-band default of `deepfilternet3-noise-filter` 1.3.0), \(L=960\), \(R=480\). These are lesson numbers for the arithmetic, not a claim that Mezon’s unpublished graph uses this exact pair.

$$
T_{\mathrm{hop}}=\frac{480}{48000}=10\,\mathrm{ms},\qquad
\frac{f_s}{R}=100\ \mathrm{hops/s},\qquad
T_{\mathrm{win}}=\frac{960}{48000}=20\,\mathrm{ms}.
$$

Overlap is \((L-R)/L=1/2\). A causal implementation cannot run the first analysis FFT until 960 samples have arrived, so the buffering delay before that first transform is 20 ms. We will call that the algorithmic delay of *filling the analysis window*. Releasing samples earlier, or holding an extra look-ahead hop, changes the constant; it does not change the hop rate. Two transforms per hop (forward and inverse) give \(2\times 100=200\) FFTs per second per channel. The hop budget is 10 ms of wall clock. At 48 kHz a 128-sample AudioWorklet quantum is \(128/480=0.267\) of a hop, so you need \(480/128=3.75\) quanta to fill \(R\), and \(960/128=7.5\) quanta to fill \(L\). `DeepFilterNet3Core` still has to be fed on whatever hop the model card states; this count is how you check that card against the callback.

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

## Mini-lab

**Goal.** Count hops per second and the analysis-window delay for \(L=960\), \(R=480\) at 48 kHz.

```python
fs, L, R = 48_000, 960, 480
hop_ms = 1_000 * R / fs
win_ms = 1_000 * L / fs
hops_per_s = fs / R
ffts_per_s = 2 * hops_per_s
print(f"hops_per_s={hops_per_s:.0f} hop_ms={hop_ms:.1f} win_ms={win_ms:.1f}")
print(f"ffts_per_s={ffts_per_s:.0f} algo_delay_ms={win_ms:.1f}")
```

**Expected.** `hops_per_s=100 hop_ms=10.0 win_ms=20.0`, then `ffts_per_s=200 algo_delay_ms=20.0`. The delay printed here is the time to collect one analysis window, not a full-product mouth-to-ear figure.

**Failure modes.** Setting algorithmic delay to the hop (10 ms) and forgetting the window must fill first. Counting one FFT per hop when the inverse is also on the clock. Copying \(L\) and \(R\) onto a model card that documents a different pair.

## Mini exercises

1. \(f_s=16\,\mathrm{kHz}\), \(R=256\): hop ms and hops/s?
2. Budget \(T_{\mathrm{proc}}\) for RTF 0.4 at that hop.
3. 128-sample quantum at 48 kHz: how many quanta to fill a 10 ms hop?
4. List state that must persist across hops for STFT-NS.
5. Sketch a profiler plan separating STFT vs neural vs ISTFT time.

### Answer hints

1. \(256/16000=16\,\mathrm{ms}\), so hops/s \(=1000/16=62.5\).
2. RTF 0.4 on a 16 ms hop allows \(6.4\,\mathrm{ms}\) of processing.
3. A 10 ms hop at 48 kHz is 480 samples, and \(480/128=3.75\) quanta. You accumulate four quanta and still have a remainder unless the ring buffer stores the extra 0.25.
4. OLA tail, analysis window, hop counter, and any recurrent state inside the suppressor.
5. Three timers around analysis FFT, the neural forward, and iFFT plus overlap-add, reported as p95 over at least a few thousand hops.

## Further reading

- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — STFT and real-time configuration sections. Reference code: https://github.com/Rikorose/DeepFilterNet.
- MDN AudioWorkletProcessor documentation.
- WebRTC APM overview (processing in framed blocks).
