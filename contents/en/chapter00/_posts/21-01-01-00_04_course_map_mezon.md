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

![A LiveKit track processor drawn as the public slot where a noise filter can sit]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. The drawing is only the public integration slot: a TrackProcessor on a media track. It does not reveal private Mezon internals.*

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

- Repository: https://github.com/mezonai/mezon-noise-suppression (`mezonai/mezon-noise-suppression`)
- npm package: `deepfilternet3-noise-filter` **1.3.0**
- Public classes named on that surface: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`
- Public control: `setSuppressionLevel(0–100)`
- Product default rate: **48 kHz full-band**
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

Calling `setSuppressionLevel` is a one-line product control. Explaining it is a chapter-map question: the integer chooses an operating point on a trained gain or mask (Ch. 03–04), the 48 kHz default fixes Nyquist and hop arithmetic (Ch. 01–02), and the processor still has to finish inside the audio callback (Ch. 05). The LiveKit figure above is a preview of where `DeepFilterNoiseFilterProcessor` can sit on a track (Ch. 07). Nothing in that drawing authorizes a guess about unpublished buffers inside the instructor tree.

### How this site is organized

Lessons live under `contents/{en,vi}/chapterXX/_posts/` with YAML front matter (`chapter`, `order`, `lang`, `draft: false`). English and Vietnamese are parallel; study in either language, but keep terminology consistent (STFT, hop, RTF, SI-SDR are shared).

## Worked example — mapping a bug to a chapter

Symptom: “NS output has robotic warble every 10 ms.”

Possible chapter triage:

1. **02** — hop/window/OLA mismatch or wrong ISTFT COLA.
2. **01** — interpreting FFT bins incorrectly after resampling.
3. **05** — underruns causing repeated frames.
4. **04** — over-aggressive periodic masking (model) — *last*, after pipeline hygiene.

This triage habit is the point of the course map. A 10 ms warble is \(100\,\mathrm{Hz}\) because \(1/0.010=100\). That number points at hop-rate amplitude modulation (Ch. 02) before it points at a bad checkpoint (Ch. 04). The mini-lab turns the same arithmetic into a pass/fail on p95 processing time.

## Common pitfalls

1. Jumping to Ch. 04 weights before securing sample-rate and mono downmix correctness.
2. Treating the npm package name as proof of a particular unpublished model graph.
3. Studying only EN or only VI and missing fixes in one locale (contribute both when you improve a lesson).
4. Skipping Ch. 08 and declaring victory from one café demo.

## Mini-lab

**Goal.** Tie the “warble every 10 ms” bug to a hop at the 48 kHz product default, and gate it on p95 processing time.

```python
fs, hop = 48_000, 480
hop_ms = 1_000 * hop / fs
warble_hz = 1_000 / hop_ms
print(f"hop_ms={hop_ms:.1f} warble_if_cola_fails_hz={warble_hz:.0f}")
for p95_ms in (6.0, 12.0):
    print(p95_ms, p95_ms < hop_ms)
```

**Expected.** `hop_ms=10.0 warble_if_cola_fails_hz=100`, then `6.0 True`, then `12.0 False`.

**Failure modes.** Blaming `DeepFilterNet3Core` before measuring the hop. Treating a 12 ms p95 as acceptable because the mean was 4 ms. Reading the LiveKit diagram as a private architecture spec.

## Mini exercises

1. Write your background (DSP: none/some/strong; WebAudio: none/some) and choose full vs fast path.
2. From COURSE_OUTLINE.md, list the seven EN lesson titles in Chapter 01.
3. Name three public sources you are allowed to cite for DeepFilterNet behavior.
4. Draft one capstone success criterion that is *measurable* (e.g. “p95 RTF ≤ 0.5 on machine X at 48 kHz mono”).

### Answer hints

1. No DSP and no WebAudio means the full path. Strong DSP and new neural SE means the fast path, including the 01-07 checklist rather than a total skip.
2. The seven titles are the `title:` fields of `contents/en/chapter01/_posts/`, orders 1 through 7, from continuous Fourier intuition through the pitfalls checklist.
3. DeepFilterNet arXiv:2110.05588, DeepFilterNet2 arXiv:2205.05474, DeepFilterNet3 arXiv:2305.08227, plus the public README at https://github.com/mezonai/mezon-noise-suppression. The reference implementation is https://github.com/Rikorose/DeepFilterNet.
4. Name the machine, the rate (48 kHz full-band if you mean the product default), mono or the downmix rule, and a tail statistic such as p95 RTF. “Sounds cleaner” is not the criterion.

## Further reading

- This repo: `COURSE_OUTLINE.md`, `AGENTS.md`, `README.md`.
- Public GitHub README: `mezonai/mezon-noise-suppression`.
- npm landing page: `deepfilternet3-noise-filter`.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) for algorithmic context, not Mezon-specific claims.
