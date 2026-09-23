---
layout: post
title: "00-03 Real-time vs offline enhancement"
chapter: "00"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter00
lesson_type: required
draft: false
---

Shipping noise suppression is less about peak MOS on a leaderboard and more about surviving the audio thread. This lesson defines latency and RTF precisely, explains causal / streaming constraints, and lists failure modes you will debug in Mezon-like integrations.

## Learning objectives

1. Define algorithmic latency, buffering latency, and real-time factor (RTF).
2. Explain causal / streaming constraints versus offline look-ahead.
3. Relate frame size, hop size, and end-to-end delay budgets for calls.
4. List failure modes: underruns, choppy audio, clock drift, state discontinuities.
5. Apply “worst-case RTF on target devices” thinking to model choice.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Definitions: latency types + RTF with numerical drills |
| 12–28 | Causal STFT pipelines; why offline SOTA fails WebRTC/LiveKit paths |
| 28–42 | Streaming state: OLA continuity, RNN/DF hidden state |
| 42–52 | Failure modes and product SLA checklist |
| 52–60 | Mini exercises |

## Core explanations

### Three latency concepts

1. **Buffering latency** — time spent collecting samples before a frame can be processed (related to window length and hop).
2. **Algorithmic latency** — delay inherent in the algorithm (look-ahead frames, filter group delay, overlap-add reconstruction delay).
3. **System latency** — OS/audio callback quantum, JS/Wasm bridges, network jitter (out of pure DSP scope but kills products).

For interactive voice, total mouth-to-ear delay budgets are often discussed in tens of milliseconds of *additional* processing before users notice awkward turn-taking. Exact product budgets vary; the engineering rule is: **measure** on the real path.

### Real-time factor

$$
\mathrm{RTF} = \frac{T_{\mathrm{proc}}}{T_{\mathrm{audio}}}
$$

If you process 20 ms of audio in 5 ms wall-clock, \(\mathrm{RTF}=0.25\). Streaming systems need **headroom**: mean RTF of 0.9 still fails when a GC pause or thermal throttle spikes a frame to RTF 2.0.

**Worked example.** Hop \(R = 480\) samples at \(f_s = 48\,\mathrm{kHz}\) → \(T_{\mathrm{audio}} = 10\,\mathrm{ms}\). Budget RTF \(\le 0.5\) ⇒ \(T_{\mathrm{proc}} \le 5\,\mathrm{ms}\) for that hop’s STFT + model + ISTFT path (amortized).

### Causal vs offline

| Property | Offline | Real-time / streaming |
|----------|---------|------------------------|
| Future frames | yes | no (or tiny look-ahead) |
| Bidirectional recurrent / attention over whole file | common | restricted / chunked |
| Batch size | large | 1 frame / small chunk |
| Metric shopping | easy | must include latency + device RTF |

DeepFilterNet2/3 literature emphasizes **real-time / causal** design choices (see papers’ real-time sections). That is why this course anchors on the DeepFilterNet family rather than only offline diffusion SE models.

### Frames, hops, and delay

For window length \(L\) samples and hop \(R\) samples:

$$
T_{\mathrm{hop}} = \frac{R}{f_s},\qquad T_{\mathrm{win}} = \frac{L}{f_s}
$$

Overlap-add (OLA) reconstruction typically introduces delay on the order of the window / hop structure (exact constant depends on implementation). Reducing \(L\) lowers delay but hurts frequency resolution — Chapter 02 develops this tradeoff.

### Streaming state

Real-time NS is a **stateful** filter:

- Overlap-add buffers and window leftovers.
- Noise estimators / VAD state (classical).
- Recurrent or temporal convolutional state (neural), including DeepFilterNet-style temporal modules.

Cold-starting state each callback produces clicks and “pumping.” Dumping state across sample-rate changes without reset logic produces mush.

### Failure modes

1. **Underrun / glitch** — processing exceeds the callback budget; audio drops or repeats.
2. **Choppy / watery speech** — over-aggressive masking, window mismatch, or phase errors.
3. **Drift** — producer/consumer clock mismatch in ring buffers (Ch. 05).
4. **Tail artifacts** — state not flushed at end of utterance (offline eval vs call hang-up).
5. **Thermal cliffs** — RTF fine for 30 s, fails at 30 min on a phone.

## Worked example — can this model ship?

Published offline model: look-ahead 300 ms, RTF 0.15 on GPU, RTF 1.2 on target CPU laptop for 48 kHz mono.

- Call path budget: \(\le 40\,\mathrm{ms}\) algorithmic look-ahead → **fail** (300 ms).
- Even if you chop look-ahead, RTF 1.2 on CPU → **fail** without downsampling, quantization, or a smaller student model.

A DeepFilterNet-class streaming model with small hop and RTF \(\sim 0.2\)–\(0.5\) on target is in the plausible shipping region — validate on *your* device, not the paper’s.

## Common pitfalls

1. Quoting paper RTF measured offline with huge batch FFT plans.
2. Ignoring **tail latency** (p95/p99) under CPU contention.
3. Using non-causal checkpoints “just for demos” then wondering why integration lags.
4. Measuring latency with `Date.now()` across layers full of hidden buffers.
5. Forgetting that browser AudioWorklet quanta (e.g. 128 samples at 48 kHz ≈ 2.67 ms) are not the same as your STFT hop.

## Mini exercises

1. Hop 256 samples at 16 kHz: hop ms? Max \(T_{\mathrm{proc}}\) for RTF 0.25?
2. List three state tensors/buffers a streaming STFT-NS system must keep between hops.
3. Explain why mean RTF 0.4 can still glitch in Chrome under load.
4. Propose a go/no-go checklist of 5 measurements before enabling NS by default in a call product.

## Further reading

- DeepFilterNet2 / DeepFilterNet3 papers — sections on real-time / causal design.
- WebRTC APM processing graph overview (where NS sits among AEC/AGC).
- MDN AudioWorklet documentation (callback timing constraints).
