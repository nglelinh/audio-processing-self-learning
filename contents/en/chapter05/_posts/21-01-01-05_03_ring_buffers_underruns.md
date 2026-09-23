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

A DeepFilterNet hop is 480 samples. An AudioWorklet quantum is often 128. Those two clocks meet in a **ring buffer**: a fixed array plus a read index and a write index. When the reader catches the writer you get an **underrun** (a click or a hole). When the writer laps the reader you get an **overrun** (latency that grows until you drop or bypass). This lesson sizes the ring and implements both policies on an 8-sample toy.

![Circular buffer with a write index ahead of a read index]({{ site.imgurl }}/generated/ring-buffer.png)

*Figure. One fixed array. The writer advances `write_pos` as quanta arrive; the reader advances `read_pos` when a full hop is ready. Occupancy is the distance between them. The grey region is the only state that must survive the next callback. Capacity does not grow.*

## Learning objectives

You will compute occupancy and free space after a 6-sample write and a 4-sample read; implement an overrun policy that drops the oldest sample rather than allocating; and choose a power-of-two capacity for a 480-sample hop, a 128-sample quantum, and a small jitter budget without hiding an extra 100 ms of delay in the ring.

## 60-minute teaching plan

- **0–10 min** — What a click, a dropout, and a growing delay sound like.
- **10–25 min** — Indices, mask, occupancy. The toy of 6 then 4.
- **25–40 min** — Two rings around one 10 ms hop. Capacity arithmetic.
- **40–50 min** — Drop versus bypass when the writer is ahead.
- **50–60 min** — Mini-lab, exercises.

## Core explanation

### Mechanics

Store PCM in an array of length $$C$$, preferably $$C=2^m$$, so wrapping is `index & (C-1)` with no division on the audio thread. A single producer and a single consumer (SPSC) need only the two indices. Occupancy and free space:

$$
\mathrm{available}=(\mathrm{write\_pos}-\mathrm{read\_pos})\bmod C,\qquad \mathrm{free}=C-\mathrm{available}.
$$

If you keep an explicit count, as the lab does, you do not recompute the modulo on every sample; you still have to wrap the indices when you store. The producer may write $$n$$ samples only when $$\mathrm{free}\ge n$$. The consumer may read $$n$$ only when $$\mathrm{available}\ge n$$. Doing either anyway is the bug: writing past free space corrupts samples the consumer has not played, and reading past available replays stale PCM or zeros.

The figure’s grey arc is occupancy. It is streaming state. Clearing the array on every enable toggle throws away that arc and the listener hears a gap (lesson 05-04).

### Where the rings sit

```text
mic quanta (128) → ring A → gather 480 → NS hop → ring B → out quanta (128)
```

Ring A converts “3.75 quanta per hop” into an integer hop. $$480/128=3.75$$, so after three callbacks ring A holds 384 samples and the hop does not run; after four it holds 512, the hop consumes 480, and 32 remain. Ring B holds the 480-sample overlap-add burst and releases it 128 samples at a time. One ring cannot serve both clocks unless you are careful about who produces: the microphone and the model are two producers if you naively share a buffer. Give them one ring each.

### Capacity

Let hop length be $$H$$ samples, quantum $$Q$$, and $$J$$ extra hops of jitter you are willing to absorb.

$$
C \gtrsim H + J\cdot H + Q.
$$

For $$H=480$$, $$Q=128$$, $$J=2$$: $$480+960+128=1568$$, next power of two **2048** samples, $$2048/48000\approx 42.7$$ ms in that stage. $$J=3$$ lands on 2048 exactly, so the next safe power of two is **4096** (85 ms). Two stages plus the model’s 40 ms look-ahead are already a long conversation delay. Every extra factor of two is delay the user attributes to the suppressor.

### Underrun, overrun, and the two policies

| Event | Condition | What to do | What the user hears if you guess |
|-------|-----------|------------|-----------------------------------|
| Output underrun | ring B has fewer than $$Q$$ samples | Copy the dry quantum (bypass) or emit a short fade to zero | A click, or a hole of silence |
| Input overrun | ring A `free < n` | Drop the oldest unread samples, then write | A skip forward. Latency stays bounded |
| Model late | hop wall time $$> 10$$ ms (RTF p95 $$> 1$$) | Leave the already-queued output; bypass new quanta until the hop catches up | Crackles if you instead block `process` |

Blocking the audio thread to “let inference finish” turns an overrun into a priority inversion. The 2.67 ms quantum will expire while you hold the lock. Bypass and drop are both non-blocking. Bypass preserves timing and lets noise through. Drop preserves the suppressor and discards audio. Pick drop on the capture ring (old mic samples are the ones you would have played late) and bypass on the output ring (the speaker cannot be handed silence without a fade, but it also cannot wait).

### What to log

`underrun_count`, `overrun_count`, high-water occupancy, low-water occupancy. Correlate overruns with the p95 RTF from lesson 05-01. A ring that sits at 95% full is extra latency you can cut. A ring that touches zero is a click you already shipped.

## Pitfalls

- Two producers, one ring, no second synchronization story.
- Interleaved stereo written into a planar ring, or the reverse. Channel layout is part of the capacity math (two rings, or $$2C$$).
- Growing $$C$$ until the call sounds like a satellite hop. 4096 samples is already 85 ms.
- Zeroing the ring on mute and un-mute. Drain it, or crossfade (lesson 05-04).

## Mini-lab

**Goal.** On a capacity-8 ring, write 6 samples, read 4, print occupancy, then write 7 more samples under a drop-oldest overrun policy and show what survived.

```bash
python3 - << 'PY'
import numpy as np

class Ring:
    def __init__(self, cap):
        self.buf = np.zeros(cap, dtype=np.float64)
        self.cap = cap
        self.w = 0
        self.r = 0
        self.n = 0
    def free(self):
        return self.cap - self.n
    def write(self, samples):
        if len(samples) > self.free():
            raise RuntimeError("overrun")
        for v in samples:
            self.buf[self.w] = v
            self.w = (self.w + 1) % self.cap
            self.n += 1
    def read(self, k):
        if k > self.n:
            raise RuntimeError("underrun")
        out = np.empty(k, dtype=np.float64)
        for i in range(k):
            out[i] = self.buf[self.r]
            self.r = (self.r + 1) % self.cap
            self.n -= 1
        return out
    def write_drop_oldest(self, samples):
        dropped = 0
        for v in samples:
            if self.free() == 0:
                self.r = (self.r + 1) % self.cap
                self.n -= 1
                dropped += 1
            self.buf[self.w] = v
            self.w = (self.w + 1) % self.cap
            self.n += 1
        return dropped

rb = Ring(8)
rb.write([1, 2, 3, 4, 5, 6])
print("after_write6", rb.n, rb.free())
got = rb.read(4)
print("read4", got.tolist(), "occ", rb.n)
dropped = rb.write_drop_oldest([10, 11, 12, 13, 14, 15, 16])
print("dropped", dropped, "occ", rb.n)
print("next4", rb.read(4).tolist())
PY
```

**Expected**. `after_write6 6 2`, then `read4 [1.0, 2.0, 3.0, 4.0] occ 2`, then `dropped 1 occ 8`, then `next4 [6.0, 10.0, 11.0, 12.0]`. After the read, the ring held 5 and 6. Seven new samples needed one extra slot, so the oldest remaining sample (5) was dropped. 6 survived, then 10, 11, and 12.

**Failure modes**. Raising the capacity instead of dropping (latency grows without a log line). Blocking when `free < n`. Using the bypass policy but still reporting the dropped-sample numbers above — bypass would have refused the write and left occupancy at 2. Forgetting to wrap `w` and `r` with modulo 8, so sample 16 lands past the array.

## Exercises

1. **Identity.** After `write 6` and `read 4` on a fresh capacity-8 ring, what is occupancy, and which samples are still stored?
2. **Power of two.** $$H=480$$, $$Q=128$$, $$J=3$$. Compute $$H+JH+Q$$ and the next power of two. How many milliseconds is that power of two at 48 kHz?
3. **Policy.** Capture ring free space is 100 samples and the callback delivers 128. Do you drop 28 oldest samples or bypass the model? What does each choice do to latency?
4. **Two rings.** Why can the model not write its 480-sample output into ring A?

### Answer hints

1. Occupancy 2. Samples 5 and 6 remain. 1 through 4 have been consumed.
2. $$480+3\times 480+128=2048$$ exactly, so a capacity of 2048 has zero spare sample. Use 4096 if you need strict $$\ge$$. $$4096/48000\approx 85.3$$ ms per stage.
3. Drop 28 oldest on the capture ring: latency stays capped, 28 samples ($$28/48000\approx 0.58$$ ms) are skipped. Bypass: the model does not run this quantum, latency does not grow, noise is passed through. Blocking is not a third option.
4. Ring A’s producer is the microphone. A second writer races the quantum callback. Ring B is the model’s output queue.

## Further reading

- Lesson 05-01 for the p95 that predicts the overrun, and lesson 05-02 for the 128-sample producer.
- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), for the thread that must not block when `free` is zero.
- JACK or PipeWire buffer-size notes, as a second vocabulary for “period versus ring depth,” not as an API you must call.
