---
layout: post
title: "05-04 Streaming model state"
chapter: "05"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter05
lesson_type: required
draft: false
---

A streaming enhancer is a function of the current hop and of state that survived the previous hop: the STFT overlap tail, the GRU vector, the deep-filter history, and the unread samples in the ring. Reset that bundle mid-call and the next hop does not match the tail. You hear a click or a one-hop noise burst.

![Ring buffer whose unread samples are state that must survive the next hop]({{ site.imgurl }}/generated/ring-buffer.png)

*Figure. The unread arc of the ring is state: it has to be the same memory on the next callback. The same rule applies to the GRU vector and to the four past STFT frames a 5-tap deep filter still needs. Wiping any of those at a hop boundary is an impulse. Listeners hear it as a click or a short noise burst.*

## Learning objectives

You will list the state a DeepFilterNet-class hop feeds back, compute the overlap tail at the published 20 ms / 10 ms framing, and crossfade on mute instead of zeroing that tail.

## 60-minute teaching plan

- **0–10 min** — A click on enable, traced to a zeroed overlap tail.
- **10–25 min** — Inventory: ring, STFT, GRU, 5 taps, SNR gate.
- **25–40 min** — Mute, device change, underrun: three different resets.
- **40–50 min** — Long calls and drift, without inventing a paper.
- **50–60 min** — Mini-lab, exercises.

## Core explanation

### What has to be the same object next hop

| State | Size at 48 kHz | If you zero it mid-call |
|-------|----------------|-------------------------|
| Input ring | 0–479 samples waiting for a 480-sample hop | A hole, or a repeated quantum |
| OLA tail | **480 samples = 10 ms** | A 10 ms step. That is the click |
| GRU | 256 in the DeepFilterNet2 setup | Gains jump from the initial state: often a noise burst |
| Deep-filter history | 4 past frames, 96 low bins in the 2023 demo | Harmonics drop for up to 4 hops (40 ms) |
| Level normalizer | Exponential mean, 1 s decay (ICASSP features) | A level jump for about a second |
| SNR gate | Running $$\xi$$ (04-03) | Silence if you force $$\xi<-10$$ dB |
| Smoothed gains | One value per band ($$\lambda=0.6$$ in RNNoise) | A one-frame gain spike |

ONNX Runtime keeps this bundle only if the graph exposes it and you copy outputs back to the next inputs. A stateless call still returns a tensor; it is the wrong enhancer. A new session every hop also destroys RTF (05-01). One state vector, one call. Two tabs that share it will each eat the other’s update and both will click.

### What a reset sounds like

A 960-point window and a 480-point hop store **480 samples (10 ms)** that the next frame must add. If hop $$n$$ ends near amplitude 0.3 and you zero that tail, the output steps by ~0.3. That step is a click: you removed the overlap the window needed.

A GRU reset is often a burst. From zeros, the first SNR and gain estimates are whatever the initial activations emit, frequently “no speech” or “full gain,” for one or two 10 ms hops. Full gain on a noisy bin is a noise burst; a forced $$\xi<-10$$ dB gate (04-03) is a hole. Both line up with the button the user just pressed.

Hard-zeroing is the wrong mute. Crossfade wet to dry over one hop (480 samples, about 3.75 quanta of 128). Fade the samples in the ring, not the hidden units, if the GRU was already warm.

### Policies

1. **Cold start.** Zeros are correct before the first audible hop. Run a few silent hops before the call so the 1 s normalizer leaves exact zero.
2. **Enable.** Do not clear a tail that already holds dry audio. Crossfade dry to wet over 10–20 ms. Keep the GRU that warmed during bypass.
3. **Disable.** Crossfade wet to dry and freeze the GRU. Zeroing it makes the next enable a burst.
4. **New device or sample rate.** Full reset and a new hop length. A 44.1 kHz quantum into a 48 kHz STFT will not fade into correctness.
5. **Underrun.** Bypass (05-03) until the output ring holds a hop, then fade. Zeroing the tail without a fade clicks at the moment you were hiding a click.

### Long calls

A 45-minute call at a 10 ms hop is $$45\times 60\times 100=270\,000$$ GRU updates. Drift is a slow walk of that vector (dullness or pumping), distinct from a one-hop click. Lesson 04-05 names Fast-ULCNet only as a shortlist entry for long-stream discussion; no paper is cited here. Blend state toward zero over a few hundred milliseconds of silence. An instant blend is a reset. Compare a calibration clip at minute 1 and minute 40.

### Feedback loop

```text
state = initial   # zeros only before audio starts
for hop in stream:
    y, state = model(hop, state)
    emit y
```

Check shapes once: GRU in and out (256 in the DF2 setup), four past complex frames below the deep-filter cutoff, one 480-float tail. A mismatched binding reads the next tensor and sounds like a bad model.

## Pitfalls

- A new inference session per hop (state gone, RTF gone).
- One state object shared by two tabs.
- Seeking an offline file without a reset, so file two inherits file one’s GRU.
- Assuming a reloaded worklet kept its WASM state. A new module is a cold start.

## Mini-lab

**Goal.** Hear the reset in a number. Build a two-hop overlap tail of 4 samples (a toy stand-in for the 480-sample tail), emit the sum, then zero the tail and emit again.

```bash
python3 - << 'PY'
import numpy as np

def ola(prev_tail, frame):
    # frame layout: [overlap_with_previous | new_tail]
    mixed = prev_tail + frame[: len(prev_tail)]
    new_tail = frame[len(prev_tail) :].copy()
    return mixed, new_tail

frame0 = np.array([0.2, 0.2, 0.4, 0.4])  # tail that hop 1 will need
frame1 = np.array([0.4, 0.4, 0.1, 0.1])
mixed, tail = ola(frame0[2:], frame1)
print("continuous", mixed.tolist(), "tail", tail.tolist())
mixed_reset, tail_reset = ola(np.zeros(2), frame1)
print("after_zero_tail", mixed_reset.tolist())
print("step", float(mixed[0] - mixed_reset[0]))
PY
```

**Expected**. `continuous [0.8, 0.8] tail [0.1, 0.1]`, `after_zero_tail [0.4, 0.4]`, `step 0.4`. The continuous path adds the previous tail (0.4, 0.4) onto the next frame’s overlap. Zeroing the tail drops that contribution and the output steps by 0.4 on those samples. Scale 0.4 up to a real 480-sample hop and the step is a click. A GRU reset is the same experiment with a vector you cannot plot as easily: the first hop after the zero is an untrained transient, which comes out as a click or a noise burst.

**Failure modes**. Zeroing `tail` “to be safe” on every hop and shipping a click on every hop. Resetting on mute without the crossfade. Sharing `tail` across two streams so each hop adds the other stream’s overlap. Treating the 0.4 step as an RTF problem — the CPU was on time; the state was wrong.

## Exercises

1. **Inventory.** For a DF3-style hop, list five state objects and the owner (worklet field, ONNX input, ring).
2. **Click length.** Window 960, hop 480, sample rate 48 kHz. How many milliseconds of tail did a hard reset delete?
3. **Policy.** Write the mute, unmute, and switch-mic actions in one sentence each. Which one is allowed to zero the GRU?
4. **Drift versus reset.** A user reports a click at the moment NS is enabled, and a different user reports dull audio after 40 minutes. Which bug is state reset, and which is drift?

### Answer hints

1. Input-ring occupancy, 480-float OLA tail, GRU (256 in the DF2 setup; confirm on the ONNX I/O), four frames of deep-filter history, and the ERB running mean. The worklet owns the rings; the graph I/O owns the GRU if it is an input.
2. $$480/48000=10$$ ms of audio. That is the click’s length, not an RTF.
3. Mute and unmute: crossfade 10–20 ms and freeze the GRU. Switch-mic or sample-rate change: zero off-air, warm up on silence, then open the mic. Only that third case zeros the GRU.
4. A click at enable is a reset. Dull audio after 40 minutes is drift ($$240\,000$$ hops) or thermal RTF. Zeroing mid-sentence does not fix drift.

## Further reading

- Lessons 04-02 and 04-03 for the 5-tap history, the 256-wide GRU in DeepFilterNet2, and the SNR gate in [arXiv:2305.08227](https://arxiv.org/abs/2305.08227).
- Lesson 05-03 for the ring that holds the tail between 128-sample quanta.
- ONNX Runtime I/O binding docs, for feeding state tensors back without rebuilding the session.
- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), for processor lifetime: a new worklet is a new state, and the first hop is a cold start.
