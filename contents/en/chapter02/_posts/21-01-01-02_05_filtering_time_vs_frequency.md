---
layout: post
title: "02-05 Filtering in time vs frequency"
chapter: "02"
order: 5
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Noise suppression is filtering under uncertainty. Sometimes you FIR/IIR in time; sometimes you multiply STFT bins; sometimes a network predicts those multiplications. This lesson compares domains so you pick tools deliberately.

## Learning objectives

1. Contrast time-domain LTI filtering with STFT-domain multiplicative gains.
2. Explain circular vs linear convolution and why OLA/OLS exist.
3. Relate classical Wiener / spectral subtraction gains to STFT filtering.
4. Describe when time-domain methods still win (DC block, click suppression heuristics).
5. Avoid illegal “filter” ops that break streaming COLA.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | LTI convolution review; frequency response |
| 12–28 | STFT-domain gains as time-varying filters |
| 28–42 | Convolution via FFT; OLA/OLS |
| 42–52 | NS examples: high-pass, Wiener gain, neural mask |
| 52–60 | Exercises |

## Core explanations

### Time-domain LTI filter

$$
y[n]=(h*x)[n]=\sum_k h[k]x[n-k]
$$

Frequency response \(H(e^{j\omega})\) multiplies DTFT of \(x\) if \(h\) is fixed. Great for DC blockers, fixed shelving EQ, anti-alias low-passes. Bad alone for non-stationary noise that needs time-varying behavior.

### STFT-domain multiplicative processing

Per frame: \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\). If \(G\) changes slowly, this approximates a slowly time-varying filter. If \(G\) jumps every hop/bin independently, you get musical noise and COLA stress.

Classical **spectral subtraction** and **Wiener filtering** (Ch. 03) are recipes for \(G\). Neural masks learn \(G\) (or richer deep filters).

### Convolution via FFT

To apply a long FIR \(h\) efficiently: FFT multiply by \(H\), iFFT — but block-wise with **overlap-add** or **overlap-save** to realize *linear* convolution. Naively multiplying per-frame STFT by a fixed \(H\) without care is not always identical to the same FIR in time — windowing leaks.

### Time vs frequency: decision guide

| Need | Prefer |
|------|--------|
| Fixed mild EQ / DC remove | small IIR/FIR time-domain |
| Non-stationary NS | STFT + adaptive/neural \(G\) |
| Ultra-low CPU click gate | time-domain detector + attenuator |
| Linear long reverb FIR | FFT OLA/OLS convolution |

### DeepFilterNet tie-in

Deep filtering predicts filters across frequency (and temporal context) on complex STFT coefficients — still “frequency-domain filtering,” but richer than diagonal \(G(\ell,k)\). Time-domain waveform networks exist in literature; this course’s product alignment emphasizes STFT-centric DeepFilterNet-class pipelines.

## Worked examples

### DC blocker

One-zero filter \(y[n]=x[n]-x[n-1]\) (simplified) high-passes; cheap pre-NS. Does not remove café babble.

### Wiener cartoon

$$
G(k)=\frac{P_x(k)}{P_x(k)+P_n(k)}
$$

Estimate powers from STFT magnitudes; apply as gains; ISTFT. Non-stationary \(P_n\) estimation is the hard part.

### Illegal op

Zeroing random bins each hop without smoothing → birdies. Time-domain equivalent would be a wildly varying impulse response — audible artifacts.

## Common pitfalls

1. Assuming STFT gain multiply == arbitrary FIR exactly.
2. Using very long FIR in time on the audio thread without FFT acceleration.
3. Cascading unrelated high-pass + NS without measuring speech loss.
4. Applying linear-phase FIR with huge group delay in a call path.
5. Forgetting real-time causality when designing “cool” offline filters.

## Mini exercises

1. Give one filter better in time-domain before NS.
2. Why do unsmoothed per-bin gains click/twitter?
3. OLA vs OLS: one-sentence distinction.
4. If group delay is 30 ms from a linear-phase FIR, is it call-safe?
5. Sketch how a neural mask is still a filter \(G(\ell,k)\).

## Further reading

- Oppenheim & Schafer — filtering, FFT convolution, STFT processing.
- Classical speech enhancement surveys (Wiener / spectral subtraction) as bridge to Ch. 03.
- DeepFilterNet papers — deep filtering formulation.
