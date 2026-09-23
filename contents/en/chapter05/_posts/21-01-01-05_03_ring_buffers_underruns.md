---
layout: post
title: "05-03 Ring buffers and underruns"
chapter: "05"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter05
lesson_type: required
draft: false
---

Real-time audio is a **producer–consumer** problem. Capture produces samples; the NS consumer needs hop-sized blocks; the playback side needs continuous output. **Ring buffers** absorb jitter; when they empty or overflow you hear **underruns** / overruns. This lesson builds the data-structure intuition, capacity planning, and glitch triage for Mezon-like pipelines.

## Learning objectives

You will implement a SPSC ring buffer mentally (indices, capacity power-of-two), size buffers from hop and jitter budgets, distinguish underrun vs overrun symptoms, and write a triage checklist for crackles under load.

## 60-minute teaching plan

- **0–10 min** — Listen to underrun vs clipping vs NS distortion (narrative).
- **10–25 min** — Ring buffer mechanics; SPSC rules.
- **25–40 min** — Capacity math; multi-stage pipes (capture → hop → NS → OLA → out).
- **40–50 min** — Underrun counters; adaptive bypass.
- **50–60 min** — Pitfalls, exercises.

## Core explanation

### Mechanics

A ring buffer stores PCM in a circular array with `write_pos` and `read_pos`. For single-producer single-consumer (SPSC) without locks (or with atomics on SAB):

- Producer writes if free space ≥ $$n$$.
- Consumer reads if available ≥ $$n$$.
- Capacity typically $$2^m$$ for mask indexing: `index & (cap - 1)`.

```text
available = write_pos - read_pos          # careful with unsigned wrap
free      = capacity - available
```

### Pipeline stages

```text
mic quanta  →  [ring A]  →  hop gather  →  NS model  →  [ring B]  →  out quanta
```

- **Ring A** absorbs callback size ≠ hop size.
- **Ring B** absorbs NS producing hop bursts into smaller render quanta.
- Too small → underrun; too large → latency (algorithmic + buffering).

### Capacity planning sketch

Let hop = $$H$$ samples, quantum = $$Q$$ samples, target jitter absorb = $$J$$ frames of hops.

$$
C \gtrsim H + J\cdot H + Q.
$$

Example: $$H=480$$, $$Q=128$$, $$J=2$$ → order of ~1200+ samples capacity **per stage**, rounded to power-of-two (2048). Tune by measurement.

### Underrun vs overrun

| Event | Cause | Sound |
|-------|-------|-------|
| Underrun (output) | Consumer starved | clicks, dropouts, silence holes |
| Overrun (input) | Producer too fast / consumer stuck | delayed audio, then sudden jumps if you drop |
| NS overtime | RTF spike | same as underrun if output ring empties |

### Soft fail strategies

1. **Bypass** NS for $$N$$ frames when late (copy input→output).
2. **Drop** oldest input if capture ring overflows (better than unbounded latency).
3. **Never block** the audio thread waiting for model warm-up—pre-buffer or pass-through until ready.

### Diagnostics

Maintain `underrun_count`, `overrun_count`, `max_fill`, `min_fill`. Plot fill level over a call. Correlate with RTF_p95 from 05-01.

## Pitfalls

- Using the same ring from two producers without a concurrent design.
- Forgetting channel interleaving vs planar layouts.
- “Fixing” underruns by enlarging buffers until latency feels like a satellite call.
- Clearing the ring on every enable toggle (causes a glitch)—drain gracefully.

## Exercises

1. **Code.** Implement a float SPSC ring in Python or Rust with unit tests for wrap-around.
2. **Size.** Compute power-of-two capacity for $$H=480$$, $$Q=128$$, $$J=3$$.
3. **Glitch lab.** Artificially sleep past the deadline in a toy callback; observe underrun counters.
4. **Design.** Specify ring A/B capacities for Mezon web DF3 path in a short design note.

## Further reading

- Classic lock-free SPSC queue references (e.g. engineering articles on circular buffers in audio).
- Web Audio / game-audio underrun discussions (MDN + browser bug trackers as phenomenology).
- JACK / PipeWire latency docs — mental models for buffer depth vs latency.
