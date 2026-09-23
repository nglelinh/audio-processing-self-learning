---
layout: post
title: "06-02 Quantization for speech models"
chapter: "06"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter06
lesson_type: required
draft: false
---

**Quantization** shrinks weights and often speeds SE inference—critical for WASM download size and CPU RTF—but can damage speech quality or destabilize RNN state. This lesson covers INT8 / weight-only approaches at an engineering level, calibration methodology, and listening-first validation for noise suppressors.

## Learning objectives

You will distinguish dynamic vs static INT8 quantization, explain why SE models are sensitive to scale calibration, list layers that often stay FP32, and design an A/B listening + SI-SDR gate before shipping quantized weights.

## 60-minute teaching plan

- **0–10 min** — Size/RTF motivation for DF-class WASM.
- **10–25 min** — INT8 math cartoon; per-tensor vs per-channel scales.
- **25–40 min** — ORT quantization tool flow; calibration data for speech.
- **40–50 min** — What breaks: residual noise, over-attenuation, state drift.
- **50–60 min** — Pitfalls, exercises.

## Core explanation

### Cartoon math

A float weight $$w$$ maps to integer $$q$$ via scale $$s$$ (and optional zero-point $$z$$):

$$
w \approx s\,(q - z).
$$

GEMM kernels multiply integers and rescale. **Per-channel** scales for convolutions usually beat coarse per-tensor scales for quality.

### Approaches

| Mode | Idea | Pros | Cons |
|------|------|------|------|
| Dynamic quant | Activations quantized at runtime | Easy | Overhead; variable |
| Static PTQ | Calibrate activation ranges offline | Fast inference | Needs representative audio |
| QAT | Train with quant noise | Best quality | Costly |
| Weight-only | INT8/INT4 weights, FP acts | Simple size win | Smaller speed win |

For streaming SE, **static PTQ** or vendor toolchains around ORT are common starting points; QAT if quality regresses.

### Calibration for speech (not ImageNet)

Calibration sets must include:

- silence / noise-only,
- loud near-end speech,
- low-SNR café mixes,
- residual-echo-like clips if in scope,

Otherwise scales misfit and you get **pumping** or harsh residual noise. One minute of diverse DNS-style mixes is a teaching minimum; products use broader corpora.

### What often stays FP32

- Sensitive elementwise / gating ops,
- Final gain heads,
- Very small layers where INT8 overhead > benefit,
- First/last layers (common heuristic—verify empirically).

### Validation gate

1. Objective: SI-SDR / DNSMOS delta vs FP32 on a frozen eval set (Ch. 08).
2. Listening: 10+ paired clips, forced-choice.
3. Long-stream: 30 min stability (05-04).
4. RTF: confirm speedup on target device, not only model size.

faster-enhancer.c / int8 runtime papers (survey) show large RTF wins are possible with careful fused kernels—ORT PTQ may give smaller wins; measure.

## Pitfalls

- Calibrating on white noise only.
- Quantizing before verifying STFT parity.
- Ignoring overflow in state tensors.
- Shipping INT8 without documenting quality delta to support.

## Exercises

1. **Scale toy.** For weights in $$[-0.8,0.8]$$, compute symmetric INT8 scale.
2. **Calibration plan.** List 8 clip types for Mezon PTQ calibration.
3. **A/B protocol.** Design a blind listening sheet for FP32 vs INT8.
4. **ORT docs.** Skim ORT quantization docs; name the tools/APIs you’d call (no need to run yet).

## Further reading

- ONNX Runtime quantization documentation.
- Classic quantization primers (Jacob et al. Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference — well-known mobile quant paper).
- FastEnhancer / faster-enhancer.c discussions of int8 SE runtimes (survey pointers).
- DeepFilterNet model size / real-time notes.
