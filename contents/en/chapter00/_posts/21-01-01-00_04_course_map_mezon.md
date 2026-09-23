---
layout: post
title: "00-04 Course map and Mezon product context"
chapter: "00"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter00
lesson_type: required
draft: false
---

This lesson is the map and the contract: how chapters build from Fourier foundations to a Mezon-aligned capstone, what the public product surface is, and how to study without confusing “wrapper usage” with “technique mastery.”

## Learning objectives

1. Navigate the chapter map from DSP → classical NS → DeepFilterNet → realtime/on-device → product → eval → capstone.
2. Describe the mezon-noise-suppression stack at a **high level** using only public information.
3. State the pedagogical contract: teach techniques; npm `deepfilternet3-noise-filter` is a *surface*, not the syllabus.
4. Plan a study path (full vs fast-track) matching your background.
5. Know where to find advisor outline and contribution rules.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–15 | Walk COURSE_OUTLINE.md chapter table; mark prerequisites |
| 15–30 | Product context: GitHub / npm / local instructor path; do’s and don’ts |
| 30–45 | Capstone preview (Ch. 09) and evaluation mindset (Ch. 08) |
| 45–55 | Personal study plan worksheet |
| 55–60 | Mini exercises |

## Core explanations

### Chapter map (00–10)

| Ch | Theme | Why it exists |
|----|-------|---------------|
| 00 | Problem framing | Shared vocabulary, Mezon context |
| 01 | Fourier & discrete transforms (**deep**) | STFT/FFT literacy for engineers |
| 02 | Audio processing pipeline | PCM → frames → STFT → latency tradeoffs |
| 03 | Classical NS / AEC / beamforming | Priors DeepFilterNet still sits on |
| 04 | Neural SE & DeepFilterNet family | Core model ideas and successors survey |
| 05 | Real-time constraints | RTF, AudioWorklet, ring buffers, state |
| 06 | On-device inference | ONNX / tract, quantization, WASM/SIMD |
| 07 | Product integration | WebRTC, LiveKit, CDN models, npm surface |
| 08 | Evaluation | SI-SDR, DNSMOS, listening, DNS metrics |
| 09 | Capstone: Mezon NS | Techniques demonstrated end-to-end |
| 10 | References & further paths | Curated reading only |

Chapters **01** and **02** are first-class modules (seven lessons each), not a DSP “appendix.” If you skim them, later debugging will feel like superstition.

### Recommended paths

- **Full path (engineers new to DSP):** 00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09.
- **Fast path (strong DSP, new to neural SE):** 00 → skim 01–02 checklists → 04 → 05–07 → 08 → 09.
- **Product integration focus:** 00, 02-07, 05, 06, 07, 08, 09 — but still read 01-07 pitfalls.

### Mezon product context (public)

Aligned artifacts named in this course:

- Repository: `mezonai/mezon-noise-suppression`
- npm package: `deepfilternet3-noise-filter`
- Instructor local path (optional): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

**Rules of engagement**

1. Do **not** modify the product repository from course tasks.
2. Do **not** invent unpublished architecture claims; cite public README / npm docs / papers.
3. Capstone should show you can explain STFT framing, model placement, latency, and evaluation — optionally using the public package as an integration target.
4. Optional Rust native (`df-core`) paths are stretch goals (Ch. 09).

### What “techniques not wrapper” means

Being able to write:

```js
// illustrative — check current npm API before shipping
await filter.process(audioFrame);
```

is useful and insufficient. You should also be able to answer:

- What hop / window / sample rate does the pipeline assume?
- Where does algorithmic latency come from?
- What happens on stereo input?
- How do you know quality improved beyond “sounds nicer today”?

Those answers live in Chapters 01–02, 04–08 — not in autocomplete.

### How this site is organized

Lessons live under `contents/{en,vi}/chapterXX/_posts/` with YAML front matter (`chapter`, `order`, `lang`, `draft: false`). English and Vietnamese are parallel; study in either language, but keep terminology consistent (STFT, hop, RTF, SI-SDR are shared).

## Worked example — mapping a bug to a chapter

Symptom: “NS output has robotic warble every 10 ms.”

Possible chapter triage:

1. **02** — hop/window/OLA mismatch or wrong ISTFT COLA.
2. **01** — interpreting FFT bins incorrectly after resampling.
3. **05** — underruns causing repeated frames.
4. **04** — over-aggressive periodic masking (model) — *last*, after pipeline hygiene.

This triage habit is the point of the course map.

## Common pitfalls

1. Jumping to Ch. 04 weights before securing sample-rate and mono downmix correctness.
2. Treating the npm package name as proof of a particular unpublished model graph.
3. Studying only EN or only VI and missing fixes in one locale (contribute both when you improve a lesson).
4. Skipping Ch. 08 and declaring victory from one café demo.

## Mini exercises

1. Write your background (DSP: none/some/strong; WebAudio: none/some) and choose full vs fast path.
2. From COURSE_OUTLINE.md, list the seven EN lesson titles in Chapter 01.
3. Name three public sources you are allowed to cite for DeepFilterNet behavior.
4. Draft one capstone success criterion that is *measurable* (e.g. “p95 RTF ≤ 0.5 on machine X at 48 kHz mono”).

## Further reading

- This repo: `COURSE_OUTLINE.md`, `AGENTS.md`, `README.md`.
- Public GitHub README: `mezonai/mezon-noise-suppression`.
- npm landing page: `deepfilternet3-noise-filter`.
- DeepFilterNet project papers for algorithmic context (not Mezon-specific claims).
