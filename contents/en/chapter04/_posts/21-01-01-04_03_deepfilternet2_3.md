---
layout: post
title: "04-03 DeepFilterNet2 and DeepFilterNet3"
chapter: "04"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

**DeepFilterNet2** and **DeepFilterNet3** refine the original deep-filtering recipe for better quality–efficiency trade-offs and stronger real-world robustness. This lesson stays honest: we summarize **practical upgrades commonly associated** with DF2/DF3 from the published papers and ecosystem, relate DF3-style deployment to `deepfilternet3-noise-filter` / Mezon, and note **training-data / RIR sensitivity** without inventing benchmark numbers.

## Learning objectives

You will list headline upgrades from DF → DF2 → DF3 at a product-engineering level, explain why export-to-ONNX matters more than Python demo FPS, relate the npm package to the model family (wrapper ≠ algorithm), and state how room impulse response (RIR) realism in training affects deployment.

## 60-minute teaching plan

- **0–10 min** — Recap DF core (ERB + deep filter); versioning motivation.
- **10–25 min** — DF2 narrative: efficiency, training, and streaming practicality.
- **25–40 min** — DF3 narrative: further refinements; product packaging.
- **40–50 min** — Data / RIR sensitivity; what not to over-claim.
- **50–60 min** — Exercises; Mezon alignment checklist.

## Core explanation

### How to read version bumps

Treat DF / DF2 / DF3 as **generations of the same design family**:

- Same DNA: full-band, real-time, ERB + deep filtering.
- Different training recipes, network width/depth details, and sometimes loss / data pipelines.
- Deployment artifacts (ONNX, quantized weights) may lag paper names—**always pin SHA / model filename** in product docs.

### DeepFilterNet2 — engineering themes

From the DF2 paper and ecosystem (cite the paper; do not fabricate metrics):

- Stronger focus on **real-time CPU** operation with competitive quality.
- Continued use of multi-stage / multi-resolution processing in the DF family style.
- Wider adoption as a **baseline** in follow-on papers (DPDFNet builds on DF2-style backbones—04-04).

For engineers: DF2 is often the baseline you beat *or* ship when DF3 packaging is unavailable.

### DeepFilterNet3 — product themes

DF3 continues the family toward better quality and robustness for modern full-band SE. In this course’s product alignment:

- npm package name **`deepfilternet3-noise-filter`** signals a **DF3-oriented** runtime path (WASM / ONNX-style on-device inference—details in Ch. 06–07, 09).
- Your job as a student is to understand **techniques**: framing, causal state, model I/O, RTF—not only `npm install`.

**Wrapper vs model:** the package loads weights, runs inference in an audio callback-friendly way, and exposes a TrackProcessor-like API. It does **not** absolve you from knowing STFT hop, streaming state reset, or cold-start RTF.

### Export paths toward ONNX

Typical path (conceptual):

```text
training (PyTorch) → ONNX graph → ORT / WASM / tract → AudioWorklet or native
```

Pitfalls (expanded in Ch. 06): unsupported ops, dynamic axes for stream frames, RNN state I/O as graph inputs/outputs, float32 vs int8.

### Training-data and RIR sensitivity (no invented numbers)

Speech enhancers overfit to **how you simulate rooms**. DNS-style image-source RIRs differ from measured or hybrid wave/geometric simulations. Follow-on work on training DeepFilterNet with more accurate room acoustics (well-known DF3-related training paper—cite when you assign reading) reports better behavior on real rooms / ASR downstream—the qualitative lesson for Mezon:

- If users sound “over-suppressed in meeting rooms,” suspect **train/test acoustic mismatch**, not only model size.
- Prefer evaluation on **real captures** (Ch. 08 listening + DNSMOS) alongside synthetic DNS mixes.

Do **not** quote specific PESQ deltas unless you reproduce them yourself from a pinned paper table.

### Mezon alignment checklist

1. Name the model generation actually shipped (DF3 weights? custom fine-tune?).
2. Pin sample rate (often 48 kHz) and mono downmix policy.
3. Measure RTF on target devices (Ch. 05)—not laptop-only averages.
4. Document cold start (model load) vs steady-state inference.
5. Keep classical AEC (browser/WebRTC) in front when echo exists (03-04).

## Pitfalls

- Mixing DF2 and DF3 weight files with the wrong config.
- Claiming “DF3 quality” after changing STFT hop in the wrapper.
- Evaluating only on VCTK-DEMAND-style sets for a SEA-languages product.
- Ignoring over-attenuation complaints (some successors add explicit losses—04-04).

## Exercises

1. **Version table.** Build a 3-row table DF / DF2 / DF3 with columns: paper year venue (from actual citations), primary claim in one sentence, artifact you can download.
2. **Package audit.** Read `deepfilternet3-noise-filter` README; list APIs visible to an app author vs internals you still must understand.
3. **RIR thought experiment.** Give two user-visible failure modes caused by train RIRs that are too dry vs too reverberant.
4. **Export dry-run.** Sketch ONNX I/O tensors for one streaming frame + RNN states (names can be placeholder).

## Further reading

- DeepFilterNet2 paper (Schröter et al.).
- DeepFilterNet3 / official model releases and repo tags.
- Verified follow-on training-acoustics work for DF3 (assign the specific arXiv only if verified—e.g. accurate RIR training papers naming DeepFilterNet3).
- mezon-noise-suppression / `deepfilternet3-noise-filter` README (product surface).
