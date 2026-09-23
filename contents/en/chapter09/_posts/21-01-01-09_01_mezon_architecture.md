---
layout: post
title: "09-01 Mezon NS architecture tour"
chapter: "09"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter09
lesson_type: required
draft: false
---

This capstone chapter walks the **Mezon noise suppression** stack as a product case study: browser WASM DeepFilterNet3 wrapped for LiveKit, optional native Rust experiments, and the course techniques underneath. **Do not modify the product repository from course tasks** — read, sketch, and implement experiments in your own workspace.

## 60-minute teaching plan

- 0–10 min: Product goals (realtime meeting NS on-device).
- 10–30 min: Module map — npm package, WASM, model, LiveKit processor, CDN.
- 30–45 min: Map modules → course chapters 02–08.
- 45–55 min: Advisor architecture sketch exercise.
- 55–60 min: Local paths and clone etiquette.

## Learning objectives

By the end of this lesson, you can:

- Map repo modules to course chapters.
- Identify inference, I/O, and integration layers.
- Write a short architecture sketch for advisors.
- State where the optional Rust `df-core` path sits.

## Product pointers

| Artifact | Location |
|----------|----------|
| GitHub | [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) |
| npm | `deepfilternet3-noise-filter` |
| Instructor local (TS) | `/Users/nguyenlelinh/ncc/mezon-noise-suppression` |
| Optional Rust sibling | `mezon-noise-suppression-rust` (`df-core`, `df-audio`, `df-cli`) |
| Upstream model/engine | [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) |

## Layered architecture

```text
┌─────────────────────────────────────────────┐
│ App / LiveKit Room (publish, UX toggles)    │  ← Ch 07
├─────────────────────────────────────────────┤
│ DeepFilterNoiseFilterProcessor (TrackProc)  │  ← Ch 07-02
│ DeepFilterNet3Core + AudioWorklet           │  ← Ch 05
├─────────────────────────────────────────────┤
│ WASM libDF (SIMD optional)                  │  ← Ch 06
│ Model: DeepFilterNet3_onnx.tar.gz (CDN)     │  ← Ch 04, 07-03
├─────────────────────────────────────────────┤
│ DSP ideas: ERB + deep filtering, frames     │  ← Ch 02, 04
└─────────────────────────────────────────────┘

Optional native:
┌──────────────────┐
│ df-cli / df-audio│
│ df-core frame API│  ← Ch 09-03 (stretch)
└──────────────────┘
```

### Inference layer

- ONNX/tar weights from DeepFilterNet3
- Executed via WASM build of upstream `libDF` (product path)
- Future/native: tract or ORT / libDF in Rust

### I/O layer

- Mic track → worklet frames (often 480 samples @ 48 kHz / 10 ms in stub docs)
- Ring buffers / underrun policy (Ch 05)

### Integration layer

- LiveKit `setProcessor`
- CDN `assetConfig`
- Enable / suppression level UX

## Architecture sketch for advisors (template)

```markdown
## Mezon NS — architecture sketch
- Goal: on-device uplink NS for LiveKit meetings
- Data path: mic → TrackProcessor → DF3 WASM → publish
- Assets: WASM + ONNX tar via CDN v2 layout (≥1.2.0)
- Controls: setEnabled, setSuppressionLevel
- Eval: SI-SDR (synth), DNSMOS (real), AB listening, RTF
- Non-goals: cloud inference of raw audio; editing product repo in homework
- Stretch: df-core parity with process_frame goldens
```

## Course chapter ↔ module checklist

| Chapter | What to look for in Mezon |
|---------|---------------------------|
| 02 | Frame length, sample rate, overlap behavior |
| 03 | Interaction with browser AEC/NS flags |
| 04 | Why DF3; attenuation / post-filter knobs |
| 05 | Worklet, realtime budget |
| 06 | WASM SIMD, packaging |
| 07 | Processor + CDN |
| 08 | How you will prove a change |

## Common pitfalls

1. Treating README usage as full architecture understanding.
2. Skipping asset/version pairing (`v2` WASM with old model layout).
3. Planning capstone edits inside the shared product tree.

## Exercises

1. Fill the advisor sketch template with your own words (≤1 page).
2. Draw the sequence diagram for `connect` → asset load → `setProcessor` → toggle level.
3. List three telemetry events you would add without uploading audio.
4. Compare TS WASM path vs Rust `df-core` stub responsibilities.

## Further reading

- Package + GitHub README (LiveKit + CDN sections).
- Upstream DeepFilterNet README / ICASSP 2022 paper (arXiv:2110.05588).
- Course Chapters 03–07 as prerequisites.
