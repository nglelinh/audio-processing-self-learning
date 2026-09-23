---
layout: post
title: "02-06 Spectrograms: reading speech and noise"
chapter: "02"
order: 6
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Spectrograms are the shared language of speech engineers. This lesson trains you to read speech structure, noise types, and NS artifacts visually — and to avoid lying dB scales.

## Learning objectives

1. Interpret spectrogram axes (time, frequency, dB color).
2. Recognize voiced harmonics, formants, fricatives, and silence.
3. Identify stationary noise floors, bursts, babble, and music.
4. Spot common NS artifacts (musical noise, over-suppression, warble).
5. Use spectrograms responsibly alongside listening and metrics.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Anatomy of a spectrogram plot |
| 10–28 | Speech patterns gallery (describe without audio) |
| 28–42 | Noise gallery + mixture reading |
| 42–52 | Before/after NS artifact reading |
| 52–60 | Exercises |

## Core explanations

### Axes and scaling

- **X:** time (s) or frame index.
- **Y:** Hz (linear) or Mel/ERB (perceptual).
- **Color:** usually \(20\log_{10}|X(\ell,k)|\) with a floor clamp.

Always record: \(f_s\), window, hop, FFT size, dB range (e.g. −80..0 dB). Without these, screenshots are not science.

### Speech landmarks

| Pattern | Look |
|---------|------|
| Voiced vowel | Harmonic striations; dark formant bands |
| Pitch change | Striations tilt / spacing change |
| Plosive | Vertical broadband burst + closure gap |
| Fricative | High-frequency noisy cloud |
| Silence | Near floor (mic noise remaining) |

### Noise landmarks

| Noise | Look |
|-------|------|
| HVAC | Low-frequency persistent ridge |
| Fan hiss | Elevated broadband floor |
| Keyboard | Thin vertical spikes |
| Babble | Speech-like but unruly competing structure |
| Music | Stable harmonic stacks unlike speech formant motion |

### Artifact landmarks after NS

| Artifact | Look / sound |
|----------|--------------|
| Musical noise | Speckled isolated bins in time |
| Over-suppression | Missing fricative clouds; muffled |
| Hop warble | Periodic amplitude stripes at hop rate |
| Residual reverb | Vertical smearing lasting after speech |

### Good practice

Spectrogram **supports** listening and SI-SDR/DNSMOS (Ch. 08); it does not replace them. A pretty spectrogram can still sound bad (phase issues invisible on mag plots).

## Worked examples

### Parameter stamp

“48 kHz, Hann 20 ms, hop 10 ms, N=1024, dB −70..0” — reproducible.

### Misread

Bright low-frequency bar might be DC bias, not “noise the model failed.” High-pass before plotting if diagnosing NS.

### Babble vs target

Both show harmonics; target often louder/closer (higher SNR tracks). Single-channel NS struggles — spectrogram sets expectations.

## Common pitfalls

1. Comparing plots with different dB color ranges.
2. Using Mel plots to debug linear-STFT bin bugs.
3. Declaring victory from a quieter floor alone (speech may be damaged).
4. Ignoring that phase artifacts are mag-invisible.
5. Ultra-long windows that make everything look “stationary.”

## Mini exercises

1. Sketch a spectrogram cartoon of “hello” in noise.
2. How would 10 ms hop COLA failure appear?
3. Why clamp log floors?
4. Name two cues distinguishing music interference from voiced speech.
5. What metadata must accompany a spectrogram in a bug ticket?

## Further reading

- Speech processing textbooks’ spectrogram chapters (standard DSP/speech notes).
- DNS Challenge visualization examples (dataset pages).
- DeepFilterNet paper figures (read axes carefully).
