---
layout: post
title: "00-01 Why real-time noise suppression matters"
chapter: "00"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter00
lesson_type: required
draft: false
---

Real-time noise suppression (NS) is the product constraint that decides whether a voice call feels usable in an open office, on a motorcycle ride, or next to a mechanical keyboard. This lesson frames the *problem*, not the algorithms: who cares, what “good” means, and how this course connects to Mezon’s public noise-suppression work.

## Learning objectives

By the end of this lesson (~60 minutes) you should be able to:

1. Explain why single-channel NS is a first-class requirement in VoIP, conferencing, and embedded voice UIs.
2. Separate three enhancement goals: **intelligibility**, **perceptual quality**, and **ASR-friendly** input.
3. Distinguish real-time / causal enhancement from offline batch enhancement in product terms (latency, RTF).
4. Locate this course relative to the public Mezon stack (`mezonai/mezon-noise-suppression`, npm `deepfilternet3-noise-filter`) without inventing unpublished internals.
5. State what this course will *not* treat as primary (full AEC/AGC product stacks).

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–8 | Warm-up: listen mentally to three scenes (office HVAC, street, keyboard) and list what breaks in a call |
| 8–20 | Product goals: intelligibility vs quality vs ASR; map each to a failure mode |
| 20–35 | Real-time constraints: frame delay, RTF, why offline SOTA often cannot ship |
| 35–48 | Mezon / DeepFilterNet product context (public surface only) and course scope |
| 48–60 | Mini exercises + discussion of pitfalls |

## Core explanations

### Noise as a product constraint

In consumer and enterprise voice products, noise is not an academic additive disturbance \(n(t)\). It is a **user-visible SLA**:

- **Office / HVAC**: quasi-stationary low-frequency rumble; easy for classical estimators, annoying if left alone.
- **Street / café**: non-stationary bursts; classical noise-floor trackers lag; neural models earn their keep.
- **Keyboard / mouse**: impulsive, broadband clicks that punch through speech formants.
- **Babble**: competing speech; the hardest single-channel case because the “noise” lives in the same time–frequency patterns as the target.

A usable NS block must reduce these without turning speech into watery artifacts, without adding tens of milliseconds of delay that destroy conversational turn-taking, and without burning so much CPU that an AudioWorklet callback underruns.

### Three enhancement goals (do not collapse them)

Engineers often say “make it cleaner.” That hides three different objectives:

1. **Intelligibility** — can a listener (or ASR) recover words? Spectral distortion that removes consonants can *look* quieter on a spectrogram and still destroy intelligibility.
2. **Perceptual quality** — MOS / DNSMOS-style pleasantness: less hiss, less musical noise, natural timbre.
3. **ASR upstream** — some pipelines optimize word-error rate; aggressive NS that helps humans can *hurt* ASR if it removes cues the recognizer relies on.

Classical metrics (SI-SDR) and listening metrics (DNSMOS) disagree often enough that product teams must pick a primary goal. This course emphasizes **real-time conversational quality** aligned with Mezon-style browser / WebRTC paths, while teaching evaluation tools in Chapter 08.

### Real-time vs offline (preview; deep dive in 00-03)

Offline enhancement may use the whole utterance, bidirectional context, and large networks. Real-time enhancement is **causal**: at time \(t\) you may only use audio up to \(t\) (plus a small intentional look-ahead budget).

Two numbers dominate design reviews:

- **Algorithmic / buffering latency** (ms): how long until the cleaned sample leaves the pipeline.
- **Real-time factor (RTF)**: wall-clock processing time divided by audio duration. For streaming, you need worst-case RTF \(\ll 1\) on the *target* device, not the mean on a laptop CPU.

If a published model needs 200 ms look-ahead and RTF 0.8 on a phone CPU, it is research-interesting and product-dead for interactive calls.

### Mixture model (one equation to keep)

Single-channel observation in the time domain:

$$
y(t) = x(t) + n(t)
$$

or, after an STFT,

$$
Y(\ell,k) = X(\ell,k) + N(\ell,k)
$$

where \(\ell\) is the frame index and \(k\) the frequency bin. Almost every classical and neural NS method is a strategy for estimating \(X\) (or a mask / filter that recovers \(X\)) from \(Y\) under real-time constraints. Convolutional distortion (reverb) is a *related but separate* problem:

$$
y(t) = (x * h)(t) + n(t)
$$

Do not claim a single-channel NS model “solves reverb” unless evaluation explicitly includes it.

### Mezon product context (public facts only)

This course is aligned with Mezon noise-suppression product work:

- GitHub organization/repo: **`mezonai/mezon-noise-suppression`**
- npm package surface commonly referenced in the outline: **`deepfilternet3-noise-filter`**
- Instructor local checkout (do not require students to have this path): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

**Teach techniques** (DSP → classical NS → DeepFilterNet family → realtime/on-device → eval → integration), not “how to call one npm wrapper.” Capstone Chapter 09 asks you to demonstrate understanding of the pipeline, not to reverse-engineer unpublished internals. Anything not documented in public READMEs, papers, or npm docs is out of scope for claims.

### Scope boundaries

| In scope | Out of scope as primary syllabus |
|----------|-----------------------------------|
| Framing, STFT, classical NS, DeepFilterNet ideas, RTF, ORT/WASM, WebRTC/LiveKit integration patterns, metrics | Full acoustic echo cancellation (AEC) product design, multi-mic beamforming hardware, unpublished Mezon internals |
| AEC / AGC / WebRTC APM as *context* (Ch. 03) | Claiming the course replaces WebRTC APM |

## Worked example — latency budget sketch

A conferencing product targets \(\le 40\,\mathrm{ms}\) algorithmic buffering from mic callback to cleaned PCM handed to the encoder.

Assume \(f_s = 48\,\mathrm{kHz}\), frame length \(L = 480\) samples (10 ms), hop \(R = 240\) samples (5 ms), and a model that needs one frame of look-ahead.

- Buffering to assemble one analysis window of 10 ms already costs 10 ms if you wait for a full window (implementations can overlap; still, *some* buffering exists).
- Hop 5 ms means you emit a new STFT column every 5 ms — good for continuity, but CPU must finish each hop’s work within that budget on average.
- One-frame look-ahead adds another \(\sim 5\)–\(10\,\mathrm{ms}\) depending on definition.

**Numerical intuition:** at 48 kHz, 1 ms = 48 samples. A 20 ms hop is 960 samples. If your neural forward pass takes 8 ms wall-clock on device, RTF for that hop alone is \(8/20 = 0.4\) — healthy headroom. If it takes 22 ms, you will underrun unless you increase hop (latency) or shrink the model.

## Common pitfalls

1. **Optimizing SI-SDR offline** and shipping the same checkpoint for streaming without measuring causal latency and device RTF.
2. **Treating “noise reduction %”** as a metric — undefined for product QA.
3. **Assuming mono NS** works unchanged on stereo without a documented downmix policy.
4. **Blaming the neural model** when the bug is sample-rate mismatch, wrong hop, or OLA window mismatch (Ch. 01–02 checklists).
5. **Claiming Mezon-specific secrets** from reading this course — stick to public surfaces and general DeepFilterNet literature.

## Mini exercises

1. Pick a 10-second mental scene (café). List three noise events and mark each as stationary / non-stationary / speech-like.
2. Write one sentence each for intelligibility, quality, and ASR goals for a customer-support softphone.
3. Given \(f_s=16\,\mathrm{kHz}\) and hop \(R=160\) samples, compute hop duration in ms and the maximum average processing time for RTF \(= 0.5\).
4. Browse the public `mezonai/mezon-noise-suppression` README (when online) and list three *documented* capabilities — do not invent others.

## Further reading

- WebRTC Audio Processing Module (APM) documentation — noise suppression overview.
- Schröter et al., DeepFilterNet papers (INTERSPEECH / arXiv) — abstract and introduction for motivation.
- DNS Challenge overview pages (dataset and track motivation).
