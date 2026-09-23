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

Streaming SE models carry **state** across hops: STFT overlap leftovers, RNN/GRU hidden vectors, deep-filter history taps, maybe noise PSD trackers. Mismanaging state causes clicks at start, quality drift over long calls, or corruption after sample-rate changes. This lesson catalogs state types, reset policies, and long-stream stability tests.

## Learning objectives

You will list state elements in a DF-class streaming graph, design reset / flush policies for mute and device-switch events, explain long-stream drift risks for tiny RNNs, and specify a test plan covering 30+ minute calls.

## 60-minute teaching plan

- **0–10 min** — Bug story: enabling NS mid-sentence → metallic click.
- **10–25 min** — Inventory of streaming state (DSP + neural).
- **25–40 min** — Reset / warm-start / bypass transitions.
- **40–50 min** — Drift and mitigation patterns (ultra-light literature pointer).
- **50–60 min** — Pitfalls, exercises.

## Core explanation

### State inventory

| Kind | Examples | Failure if wrong |
|------|----------|------------------|
| STFT/OLA | input ring, overlap-add tail | clicks, comb filtering |
| Neural recurrent | GRU/LSTM h, c | wrong timbre, explosion |
| Deep filter taps | last $$T-1$$ spectra | transient smear |
| Classical trackers | noise PSD, $$\xi$$ | over/under suppression |
| Control | enabled, strength | sudden gain jumps |

ONNX streaming graphs often expose state as **explicit inputs/outputs** you must feed back each frame. Forgetting to wire them makes the model behave like a stateless wrong network.

### Transitions

1. **Cold start:** zeros or learned initial state; optionally run silent warm-up frames.
2. **Enable NS mid-call:** crossfade dry→wet over 5–20 ms; reset OLA carefully.
3. **Disable:** crossfade wet→dry; keep state or freeze—document choice.
4. **Device / sample-rate change:** **full reset** + reinit hop sizes.
5. **Underrun recovery:** prefer reset of OLA tails; consider soft RNN decay toward zero.

### Long-stream drift

Ultra-light models (Fast-ULCNet line) document **RNN state drift** over long inference. DF-class models can also accumulate numerical weirdness under quantization (Ch. 06). Mitigations:

- Reset or blend state toward zero during extended silence (VAD-gated),
- Periodic renormalization if theory allows,
- End-to-end tests of **≥ 30–45 minutes**,
- Capture “hour 0 vs hour 1” DNSMOS / listening spots.

### Pseudocode feedback

```text
state = zeros()
for hop in stream:
    y, state = model(hop, state)   # state in/out
    emit y
```

Unit-test that `state` shapes match ORT bindings exactly (common integration bug).

## Pitfalls

- Re-creating the ORT session every hop (destroys state *and* RTF).
- Sharing one state object across two concurrent calls (meetings with multiple tabs).
- Not resetting after seek in offline file mode (teaching labs).
- Treating WASM global memory as process-safe across worklet reloads.

## Exercises

1. **Inventory.** For DeepFilterNet-style inference, list state tensors you expect; verify against a pinned ONNX I/O dump.
2. **Click hunt.** Deliberately zero OLA tails mid-stream in a toy STFT; describe the artifact.
3. **Policy doc.** Write Mezon’s official reset policy for mute, unMute, and switch-mic events.
4. **Long-run test.** Design an automated job that runs NS 45 minutes and flags RTF_p95 and gain drift.

## Further reading

- ONNX Runtime I/O binding / stateful RNN examples.
- DeepFilterNet streaming inference code paths.
- Fast-ULCNet discussions of long-stream state behavior (survey pointer).
- AudioWorklet processor lifetime notes (MDN).
