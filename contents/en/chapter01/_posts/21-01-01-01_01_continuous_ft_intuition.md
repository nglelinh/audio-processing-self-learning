---
layout: post
title: "01-01 Continuous Fourier transform intuition"
chapter: "01"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

Speech enhancement lives in the frequency domain more often than in raw waveforms. This lesson builds continuous-time Fourier intuition so that discrete STFT code in later chapters is not a pile of magic parameters. Plan on a full hour: definitions, properties, perceptual mapping, and an engineer’s bridge toward sampling and DFTs.

![A waveform split into a few sinusoids whose sum rebuilds the original curve]({{ site.imgurl }}/generated/fourier-intuition.png)

*Figure. Frequency is a coordinate: each sinusoid is one basis tone, and the transform measures how much of that tone is in the signal.*

## Learning objectives

1. Explain frequency as rate of oscillation and as a coordinate in a signal basis.
2. State the forward and inverse continuous-time Fourier transform (CTFT) and the analysis/synthesis story.
3. Use linearity, shift, and differentiation/integration properties at an operational level.
4. Connect magnitude and phase spectra to audible percepts at a high level.
5. Explain why speech and noise often separate more cleanly in frequency than in time — and when that intuition fails.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–8 | Hook: same waveform, time vs frequency pictures; why VoIP stacks are spectral |
| 8–20 | Sinusoids, Euler, LTI eigenfunction intuition |
| 20–35 | CTFT pair; magnitude/phase; linearity & shift worked examples |
| 35–48 | Speech formants vs noise floors; phase myths; DeepFilterNet motivation pointer |
| 48–60 | Pitfalls, mini exercises, preview of sampling |

## Core explanations

### Frequency is a coordinate system

A complex sinusoid \(e^{j\Omega t}\) oscillates at radian frequency \(\Omega\) rad/s (\(f=\Omega/(2\pi)\) Hz). Real audio is real-valued, so we often write cosines and sines; complex exponentials are preferred in analysis because they are **eigenfunctions of LTI systems**: if input \(e^{j\Omega t}\) enters a stable LTI filter with frequency response \(H(j\Omega)\), the output is \(H(j\Omega)e^{j\Omega t}\). No new frequencies appear.

That is the deep reason frequency-domain NS is attractive: under additivity and approximate short-time LTI behavior, you can attenuate “noise bins” and pass “speech bins.” Reality is messier (non-stationary noise, mask errors, phase), but the eigenfunction picture explains the architecture of almost every classical NS block and of STFT-domain neural SE.

### Continuous-time Fourier transform

For a suitable continuous signal \(x(t)\),

$$
X(j\Omega) = \int_{-\infty}^{\infty} x(t)\,e^{-j\Omega t}\,\mathrm{d}t
$$

$$
x(t) = \frac{1}{2\pi}\int_{-\infty}^{\infty} X(j\Omega)\,e^{j\Omega t}\,\mathrm{d}\Omega
$$

**Analysis** (\(x\to X\)): measure how much of each frequency is present. **Synthesis** (\(X\to x\)): rebuild the waveform by integrating complex exponentials.

Polar form \(X(j\Omega)=|X(j\Omega)|e^{j\phi(\Omega)}\) with \(\phi=\arg X\):

| Quantity | Rough audible role |
|----------|--------------------|
| \(\|X\|\) | Energy distribution: vowels’ formants, hiss, rumble |
| \(\phi\) | Timing structure: attacks, pitch fine structure; careless phase damage → hollowness |

Spectrogram UIs plot magnitudes (often in dB). That trains a bad habit: “phase doesn’t matter.” For synthesis after aggressive masking, phase (or complex spectrum) handling is a first-class design choice — DeepFilterNet’s deep filtering on complex spectra exists partly because magnitude masks alone are limited.

### Properties you will actually use

**Linearity.** \(a x(t)+b y(t) \leftrightarrow a X(j\Omega)+b Y(j\Omega)\). Under \(y=x+n\), spectra add **linearly**. They do not add in dB. If you average dB magnitudes, you are doing something else.

**Time shift.** \(x(t-t_0)\leftrightarrow X(j\Omega)e^{-j\Omega t_0}\). A delay is a phase ramp. Two mics with different delays have different phases even when magnitudes match — relevant when you later read about multi-channel front-ends.

**Frequency shift / modulation.** \(x(t)e^{j\Omega_0 t}\leftrightarrow X(j(\Omega-\Omega_0))\). Useful mental model for heterodyning; also explains why periodic pitch creates harmonic stacks.

**Parseval (energy).** Time energy and frequency energy match up to convention constants. Operational moral: zeroing large spectral regions *must* reduce waveform energy — if your “NS” output has the same RMS but “looks cleaner” on a mis-scaled plot, check scaling bugs.

**Differentiation.** \(\frac{d}{dt}x(t)\leftrightarrow j\Omega X(j\Omega)\). High-frequency emphasis; related to why derivatives/pre-emphasis appear in speech features historically.

### Speech vs noise in frequency (cartoon physics)

**Voiced speech.** Quasi-periodic glottal excitation with fundamental \(f_0\) (say 80–250 Hz for many adults) produces harmonics at \(kf_0\). The vocal tract filters them into **formants** (broad peaks). On a spectrogram: horizontal striations (harmonics) and darker blobs (formants) that move with phonemes.

**Unvoiced speech.** Noise-like excitation (fricatives) shaped by the tract — energy often high-frequency. Over-suppressing highs destroys intelligibility (s, f, t).

**Stationary noise.** HVAC: low-frequency ridge. Fan hiss: flatter floor. Classical estimators shine here.

**Non-stationary / babble.** Energy comes and goes in speech-like patterns; frequency separation alone is insufficient — you need temporal models (RNN/TCN/attention over frames) as in modern SE.

### Bridge to the rest of Chapter 01

Microphones give samples. Continuous integrals become DTFT/DFT/FFT on windows. If you keep one sentence from this lesson, keep this: **frequency is a basis coefficient; STFT bins are local, windowed estimates of those coefficients.** Lesson 01-02 adds sampling; 01-03–01-05 make the discrete transforms precise; 01-06 puts FFTs on the audio thread.

## Worked examples

### Two tones and a low-pass

Let \(x(t)=\cos(2\pi\cdot 440\,t)+0.3\cos(2\pi\cdot 880\,t)\). Euler’s identity is the derivation, not a slogan:

$$
\cos\theta=\frac{e^{j\theta}+e^{-j\theta}}{2}.
$$

So the 440 Hz cosine is a pair of lines at \(\pm 440\,\mathrm{Hz}\), each with complex amplitude \(1/2\), and the 880 Hz cosine is a pair at \(\pm 880\,\mathrm{Hz}\) with amplitude \(0.3/2=0.15\). A low-pass at 600 Hz removes the octave partial and dulls brightness. NS that blindly low-passes “to remove hiss” makes the same mistake on fricatives. On a 48 kHz full-band path (the `deepfilternet3-noise-filter` default) those fricatives are allowed to live well above 8 kHz; a continuous-frequency picture that stops at telephony bandwidth will not match what the product mic can capture.

### Phase ramp from delay

Delay \(t_0=5\,\mathrm{ms}\). At \(f=1\,\mathrm{kHz}\), phase shift is \(-2\pi f t_0 = -10\pi\) radians \(= -5\) turns — i.e. \(- \pi\) after wrapping to \((-\pi,\pi]\). Magnitude unchanged. If you estimate magnitude masks from one alignment and apply them to a differently delayed buffer, reconstruction suffers.

### dB addition mistake

Speech bin magnitude 0.10, noise 0.10 (linear). Sum 0.20 if **coherent** same-phase (worst-case cartoon), or power sum \(\sqrt{0.01+0.01}\approx0.141\) for random-phase intuition in bins. In dB: \(20\log_{10}0.1=-20\,\mathrm{dB}\). You cannot say “−20 dB + −20 dB = −40 dB” for the mixture.

## Common pitfalls

1. Treating spectrogram magnitude as the whole story; ignoring phase/complex filtering.
2. Adding dB values as if they were linear amplitudes.
3. Confusing \(\Omega\) (rad/s) with \(f\) (Hz): \(\Omega=2\pi f\).
4. Assuming “more frequency resolution is always better” without latency cost (later lessons).
5. Expecting CTFT symbols to appear in code — production uses FFT windows.

## Mini-lab

**Goal.** Synthesize one second of 200 Hz + 600 Hz + 1000 Hz at 8 kHz and read the `rfft` peak bins. With \(N=f_s\), bin index equals frequency in Hz.

```python
import numpy as np

fs = 8000
t = np.arange(fs) / fs
x = (
    np.sin(2 * np.pi * 200 * t)
    + np.sin(2 * np.pi * 600 * t)
    + np.sin(2 * np.pi * 1000 * t)
)
mag = np.abs(np.fft.rfft(x))
order = np.sort(np.argsort(mag)[-3:])
print(order.tolist())
print(np.round(mag[order], 1).tolist())
```

**Expected.** `[200, 600, 1000]` and `[4000.0, 4000.0, 4000.0]`. Each unit-amplitude sine, held for an integer number of cycles, lands on one positive bin with magnitude \(N/2=4000\).

**Failure modes.** Using `np.fft.fft` and reporting a negative-frequency index as a second peak. Choosing \(N\) not divisible by the periods, then watching the peak smear off the integer bin. Reading the magnitude as the cosine’s \(1/2\) coefficient from the worked example — a sine’s `rfft` scaling is \(N/2\), not \(1/2\).

## Mini exercises

1. Write \(\sin(\Omega t)\) as complex exponentials via Euler’s formula.
2. Delay 2 ms: phase shift at 500 Hz and at 2 kHz (before wrapping).
3. Sketch cartoon spectra: voiced vowel, white noise, keyboard click, babble.
4. In one paragraph, why are complex exponentials preferred when analyzing LTI filters?
5. Give one case where time-domain methods might beat naive spectral subtraction (hint: impulsive clicks).

### Answer hints

1. \(\sin\theta=(e^{j\theta}-e^{-j\theta})/(2j)\). Two lines, opposite sign, factor \(1/(2j)\).
2. \(\Delta\phi=-2\pi f t_0\). At 500 Hz and 2 ms: \(-2\pi\cdot 0.5\cdot 2=-2\pi\) radians (one full turn). At 2 kHz: \(-8\pi\) radians, four turns. Magnitude is unchanged.
3. Vowel: harmonic stack plus formant blobs. White noise: flat. Click: broadband spike. Babble: a second, messier harmonic stack.
4. An LTI filter multiplies \(e^{j\Omega t}\) by \(H(j\Omega)\) and creates no new frequencies. A cosine splits into two such eigenfunctions.
5. A single-sample click is already spread across every bin. A short time-domain gate can catch it; a slow noise-floor tracker cannot.

## Further reading

- Alan V. Oppenheim & Ronald W. Schafer, *Discrete-Time Signal Processing* — Fourier transform overview chapters (any recent edition).
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — sinusoids as a basis, before any STFT code.
- DeepFilterNet (arXiv:2110.05588) — skim that enhancement runs in an STFT / deep-filtering domain. Motivation only in this lesson.
