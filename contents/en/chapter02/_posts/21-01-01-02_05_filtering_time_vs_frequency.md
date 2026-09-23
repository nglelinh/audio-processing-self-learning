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

Noise suppression is filtering under uncertainty. Sometimes you FIR/IIR in time; sometimes you multiply STFT bins; sometimes a network predicts those multiplications. This lesson compares domains so you pick tools deliberately. A fixed impulse response is convolution. A per-bin suppressor gain is a new multiplier every frame, and the figure used in Chapter 03 is already that second object.

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

![Left: per-bin spectral subtraction, a different gain on each frequency bin. Right: a smooth Wiener gain versus SNR, still one multiplier per bin rather than one fixed impulse response]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Figure. Both panels are per-bin gains, not a single convolution: the left bars change with the local spectrum, and the right curve assigns a different multiplier to each SNR.*

## Core explanations

### Time-domain LTI filter

$$
y[n]=(h*x)[n]=\sum_k h[k]x[n-k]
$$

Frequency response \(H(e^{j\omega})\) multiplies DTFT of \(x\) if \(h\) is fixed. Great for DC blockers, fixed shelving EQ, anti-alias low-passes. Bad alone for non-stationary noise that needs time-varying behavior.

“Fixed” is the load-bearing word. One \(h\) has one \(H(k)\) for the whole utterance. A 2-tap difference \(h=[1,-1]\) is a high-pass you can write in one line, and its magnitude response does not care whether the current frame is a vowel or a keyboard click. That is why it belongs *before* a suppressor as a DC/rumble removal, not instead of one.

### STFT-domain multiplicative processing

Per frame: \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\). If \(G\) changes slowly, this approximates a slowly time-varying filter. If \(G\) jumps every hop/bin independently, you get musical noise and COLA stress.

Classical **spectral subtraction** and **Wiener filtering** (Ch. 03) are recipes for \(G\). Neural masks learn \(G\) (or richer deep filters).

The green bars are a per-bin subtraction (each bin its own gain). The right-hand curve \(H=\xi/(1+\xi)\) is 0.5 when speech and noise powers match (\(-6\,\mathrm{dB}\)). Neither picture is the FFT of one short fixed \(h\).

### Convolution via FFT

To apply a long FIR \(h\) efficiently: FFT multiply by \(H\), iFFT — but block-wise with **overlap-add** or **overlap-save** to realize *linear* convolution. Naively multiplying per-frame STFT by a fixed \(H\) without care is not always identical to the same FIR in time — windowing leaks.

Linear convolution of an 8-point ramp with \(h=[1,-1]\) has a tail; an 8-point circular convolution wraps that tail onto sample 0 (the mini-lab’s mismatch is 8). **Overlap-add** keeps the tail and adds it into the next block. **Overlap-save** discards the wrapped edge and hops by the valid samples. A per-bin \(G(\ell,k)\) that changes every hop is a different, time-varying filter, not automatically that FIR.

### Time vs frequency: decision guide

| Need | Prefer |
|------|--------|
| Fixed mild EQ / DC remove | small IIR/FIR time-domain |
| Non-stationary NS | STFT + adaptive/neural \(G\) |
| Ultra-low CPU click gate | time-domain detector + attenuator |
| Linear long reverb FIR | FFT OLA/OLS convolution |

### DeepFilterNet tie-in

Deep filtering predicts filters across frequency (and temporal context) on complex STFT coefficients — still “frequency-domain filtering,” but richer than diagonal \(G(\ell,k)\). A diagonal gain cannot build a harmonic that the noise destroyed; a short filter along time or frequency can mix neighbors that still have phase structure. Time-domain waveform networks exist in literature; this course’s product alignment emphasizes STFT-centric DeepFilterNet-class pipelines at 48 kHz with the hop and window that match the checkpoint (lessons 02-02 and 02-04).

## Worked examples

### DC blocker

One-zero filter \(y[n]=x[n]-x[n-1]\) (simplified) high-passes; cheap pre-NS. Does not remove café babble. Its null is at DC (\(H(0)=0\)) and its peak is at Nyquist. Group delay is a fraction of a sample, so it does not eat the conversational latency budget the way a linear-phase FIR of hundreds of taps would.

### Wiener cartoon

$$
G(k)=\frac{P_x(k)}{P_x(k)+P_n(k)}
$$

Estimate powers from STFT magnitudes; apply as gains; ISTFT. Non-stationary \(P_n\) estimation is the hard part. This is the right-hand curve of the figure, one number per bin per frame. Chapter 03 derives it and the decision-directed tracker that feeds it.

### Illegal op

Zeroing random bins each hop without smoothing → birdies. Time-domain equivalent would be a wildly varying impulse response — audible artifacts. Also illegal in a call path: a linear-phase FIR whose group delay is 30 ms. The magnitude response can be perfect and the conversation still feels late, because every sample waits for future context the filter used to stay symmetric.

## Common pitfalls

1. Assuming STFT gain multiply == arbitrary FIR exactly.
2. Using very long FIR in time on the audio thread without FFT acceleration.
3. Cascading unrelated high-pass + NS without measuring speech loss.
4. Applying linear-phase FIR with huge group delay in a call path.
5. Forgetting real-time causality when designing “cool” offline filters.

## Mini-lab

**Goal.** Contrast one fixed FIR (convolution) with a per-bin Wiener gain, and see circular convolution fail to match linear convolution.

```python
import numpy as np

h = np.array([1.0, -1.0])
H = np.abs(np.fft.rfft(h, n=8))
print("fixed |H|", np.round(H, 3))

xi = np.array([0.1, 0.3, 1.0, 3.0, 10.0])  # a priori SNR, five bins
G = xi / (xi + 1.0)
print("per-bin G", np.round(G, 3))

x = np.arange(1, 9, dtype=float)
y_lin = np.convolve(x, h)
h_pad = np.zeros(8)
h_pad[:2] = h
y_circ = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(h_pad), n=8)
print("linear   ", y_lin)
print("circular ", np.round(y_circ, 5))
print("max |linear[:8] - circular|", np.max(np.abs(y_lin[:8] - y_circ)))
```

**Expected.** `fixed |H|` starts at 0 (DC null) and grows toward Nyquist. `per-bin G` is about `[0.091, 0.231, 0.5, 0.75, 0.909]` — a different shape, recomputed from SNR, not from `h`. Linear convolution ends in `-8`; circular convolution wraps that tail onto the first sample. The max absolute mismatch on the first 8 samples is `8.0`.

**Failure modes.** If the mismatch prints as 0, you zero-padded `x` as well as `h` and accidentally computed linear convolution; that hides the bug OLA/OLS exist to fix. If `G` equals `|H|`, the SNR vector was replaced by the FIR. A DC blocker that does not print a 0 in the first bin of `|H|` is not `h=[1,-1]`.

## Mini exercises

1. Give one filter better in time-domain before NS.
2. Why do unsmoothed per-bin gains click/twitter?
3. OLA vs OLS: one-sentence distinction.
4. If group delay is 30 ms from a linear-phase FIR, is it call-safe?
5. Sketch how a neural mask is still a filter \(G(\ell,k)\).

### Answer hints

1. A one-zero DC blocker, or the anti-alias low-pass in front of a 48→16 kHz downsample.
2. Each hop’s inverse transform is a different impulse response, so the OLA boundary jumps.
3. OLA keeps the convolution tail and adds it into the next block; OLS discards the time-aliased edge and hops by the valid part.
4. No for a live call: 30 ms is already a conversational delay before the encoder and the network.
5. \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\) with \(G\) predicted per bin (or a short deep filter around that bin).

## Further reading

- Oppenheim & Schafer — filtering, FFT convolution, STFT processing.
- Julius O. Smith, *Spectral Audio Signal Processing* — overlap-add and overlap-save.
- Classical speech enhancement (Wiener / spectral subtraction) as the bridge to Ch. 03. Boll, 1979, is the subtraction classic; the Wiener speech form is the next lesson.
