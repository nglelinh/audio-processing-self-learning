---
layout: post
title: "02-04 STFT / ISTFT for speech (DeepFilterNet tie-in)"
chapter: "02"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

The short-time Fourier transform is the workhorse representation for classical NS and for DeepFilterNet-class models. This lesson builds the STFT/ISTFT mental model and ties it to public DeepFilterNet pipeline ideas (ERB features, deep filtering on complex spectra) without inventing product internals.

## Learning objectives

1. Build a mental model of the STFT grid (time × frequency).
2. Contrast magnitude masks, complex masks, and deep filtering ideas.
3. State practical perfect-reconstruction conditions.
4. Map STFT parameters (rate, \(N\), hop, window) to latency and resolution.
5. Connect DeepFilterNet’s published STFT-centric design to engineering parameters.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | STFT definition; spectrogram as \(|STFT|\) |
| 12–28 | ISTFT / OLA; perfect reconstruction drills |
| 28–42 | Mag vs complex processing; deep filtering intuition |
| 42–52 | DeepFilterNet paper parameter extraction exercise |
| 52–60 | Exercises |

## Core explanations

### STFT

$$
X(\ell,k)=\sum_{n=0}^{L-1}x[n+\ell R]\,w[n]\,e^{-j2\pi kn/N}
$$

Grid: columns = time frames \(\ell\), rows = frequency bins \(k\). Speech enhancement estimates clean \(\hat{X}(\ell,k)\) from noisy \(Y(\ell,k)\).

### ISTFT

Inverse FFT per frame + synthesis window + OLA. If no modification and COLA holds, reconstruct \(x\) (delay/gain aside).

### Representations

| Representation | Contents | Typical use |
|----------------|----------|-------------|
| Complex \(X\) | real/imag or mag/phase | deep filtering, complex masks |
| Magnitude \(|X|\) | nonneg | classical Wiener, mag masks |
| Log-mag / dB | compressed | features, plots |
| ERB / Mel filterbanks | band energies | perceptual front-ends (DeepFilterNet uses ERB-scale features in papers) |

### Magnitude masks vs deep filtering (intuition)

**Magnitude mask:** \(\hat{X}=M\odot|Y|e^{j\arg Y}\) (reuse noisy phase). Cheap; phase errors on low SNR.

**Complex mask / filtering:** predict filters that mix neighboring time-frequency bins — **deep filtering** in DeepFilterNet literature applies learned filters on complex spectra to better recover structure than independent per-bin gains.

Read DeepFilterNet / DeepFilterNet2 / DeepFilterNet3 papers for the precise architecture; this lesson only needs the engineering moral: **you are modifying an STFT grid under causal constraints**, then ISTFT-ing back.

### Perfect reconstruction practice

Unit test: STFT→ISTFT without model ≈ identity. Then enable model. If identity already fails, stop.

### Parameter mapping

Extract from docs/papers:

- \(f_s\)
- window type & \(L\) / FFT \(N\)
- hop \(R\)
- causal look-ahead
- mono assumption

Translate to ms and hops/s using Ch. 01–02 formulas before integration testing with `deepfilternet3-noise-filter` or ORT.

## Worked examples

### Grid shape

1 s @ 16 kHz, \(R=256\), \(N=512\) real FFT → ~62 frames, 257 unique bins (0..Nyquist). A mask tensor might be \([1,257,62]\) or channels-first variants — match the model.

### Phase reuse limit

Low-SNR bin: noisy phase ≈ random. Magnitude mask cleans energy but residual sounds watery. Complex methods try harder — still not magic under babble.

## Common pitfalls

1. Centering frames offline but not in streaming (alignment skew).
2. Training with different hop than serving.
3. Feeding Mel features into a model that expects ERB or linear STFT.
4. Batch ISTFT on whole files in prod (latency).
5. Claiming undocumented Mezon STFT constants from this course.

## Mini exercises

1. Write STFT shapes for 2 s audio @ 48 kHz, \(R=480\), \(N=960\) (approx frames).
2. Why reuse noisy phase fails in deep noise?
3. List four parameters to copy from a DeepFilterNet config into your integrator checklist.
4. What does COLA failure sound like after ISTFT?
5. ERB vs linear STFT: one reason for ERB in speech enhancement front-ends?

## Further reading

- DeepFilterNet, DeepFilterNet2, DeepFilterNet3 papers — STFT, ERB, deep filtering sections.
- Classic STFT review notes (DSP courses).
- Oppenheim & Schafer — filter banks / STFT connections.
