---
layout: post
title: "01-02 Sampling, aliasing, and Nyquist"
chapter: "01"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

Every WebRTC track and every DeepFilterNet forward pass assumes a sample rate. Wrong rates create silent aliasing bugs that look like “model quality regressions.” This lesson makes the sampling theorem operational for speech NS engineers.

## Learning objectives

1. State the sampling theorem and the Nyquist rate / Nyquist frequency.
2. Explain aliasing with concrete audio numerics (tones and broadband noise).
3. Choose among 8 / 16 / 48 kHz thoughtfully for speech NS pipelines.
4. Describe anti-alias filtering before ADC and before decimation.
5. List resampling pitfalls when bridging browser clocks and neural model rates.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Hook: “we ran the 16 kHz ONNX at 48 kHz and quality tanked” postmortem |
| 10–25 | Impulse-train sampling; spectrum replicas; Nyquist proof sketch |
| 25–40 | Worked aliases; speech bandwidth tables; product rate choices |
| 40–52 | Anti-alias + resampling pipeline design; WebAudio/WebRTC notes |
| 52–60 | Pitfalls and exercises |

## Core explanations

### Sampling replicates spectra

Ideal impulse-train sampling with period \(T=1/f_s\):

$$
x_s(t)=x_c(t)\sum_{n=-\infty}^{\infty}\delta(t-nT)
$$

yields spectrum copies every \(f_s\) Hz:

$$
X_s(j2\pi f)=f_s\sum_{k} X_c\!\big(j2\pi(f-kf_s)\big)
$$

If the support of \(X_c\) is wider than \(f_s/2\), replicas **overlap**. The overlap region is irreversibly confused — **aliasing**.

### Nyquist criterion

If \(x_c\) is bandlimited with highest frequency \(B\) Hz, choose

$$
f_s > 2B
$$

Then an ideal low-pass (sinc interpolator) reconstructs \(x_c\) from samples \(x[n]=x_c(nT)\). Real systems approximate this with analog anti-alias filters + practical interpolators.

Definitions:

- **Nyquist rate** \(= 2B\) for a bandlimit \(B\).
- **Nyquist frequency** \(= f_s/2\) for a given sampler.

### Discrete-time frequency mapping

After sampling, digital frequency \(\omega\) (rad/sample) relates to Hz by

$$
\omega = 2\pi\frac{f}{f_s},\qquad f = \frac{\omega}{2\pi}f_s
$$

\(\omega=\pi\) always means Nyquist (Hz value depends on \(f_s\)). This is why the same FIR coefficients implement different Hz cutoffs at 16 vs 48 kHz.

### Audio bandwidth vs product rates

| Rate | Nyquist | Typical use in voice |
|------|---------|----------------------|
| 8 kHz | 4 kHz | Narrowband telephony |
| 16 kHz | 8 kHz | Wideband speech ML |
| 48 kHz | 24 kHz | WebRTC/full-band device clock |

Speech intelligibility energy is not uniform: vowels live lower; consonants need highs. 8 kHz shreds many fricatives. 16 kHz is a common **model native** rate. 48 kHz often matches **device** graphs. Your job is to resample **deliberately** between them.

### Anti-alias filters

**Analog (before ADC):** attenuate above \(f_s/2\). Cheap products with weak filters alias ultrasonic energy into the band.

**Digital (before decimation):** when going 48→16 kHz (factor \(M=3\)), low-pass near 8 kHz, *then* keep every third sample. Decimate-first is a bug.

### Resampling quality tiers

1. **Wrong:** drop/repeat samples; nearest-neighbor.
2. **Better:** linear interpolation (still poor near Nyquist).
3. **Production:** proper low-pass + polyphase resampler (libsamplerate-class, SoX, browser Offline resamplers, etc.).

Neural NS is sensitive: aliasing tones become “extra noise” the model never saw in training.

## Worked examples

### Tone alias

\(f=5\,\mathrm{kHz}\), \(f_s=8\,\mathrm{kHz}\). Nyquist 4 kHz. Fold: \(f_{\mathrm{alias}}=f_s-f=3\,\mathrm{kHz}\) (first folding). You perceive 3 kHz.

### Broadband fold

White-ish noise up to 20 kHz sampled at 16 kHz without anti-alias: energy from 8–20 kHz folds into 0–8 kHz, raising the in-band noise floor — SNR worsens *before* NS runs.

### Frame sizes at fixed 20 ms

$$
L = T\cdot f_s \Rightarrow L_{16k}=320,\quad L_{48k}=960
$$

Same latency budget, different FFT sizes and bin widths \(\Delta f=f_s/N\).

### RTF impact of rate

If compute scales roughly with samples/s (FFT + hop rate), jumping 16→48 kHz without changing hop *seconds* can cost ~3× STFT throughput. Measure; don’t guess.

## Common pitfalls

1. Running a 16 kHz-trained model on 48 kHz PCM “because higher is better.”
2. Claiming aliasing is impossible in float32 pipelines — aliasing is about rate, not bit depth.
3. Mixing 44.1 kHz media with 48 kHz graphs without a resampler node.
4. Using FFT-based resample incorrectly (block boundary clicks).
5. Forgetting anti-alias when downsampling for SI-SDR eval at another rate.

## Mini exercises

1. Nyquist frequency at 48 kHz and 16 kHz?
2. Alias of 10 kHz tone when \(f_s=16\,\mathrm{kHz}\) (express in \([0,f_s/2]\)).
3. Samples in 10 ms at 8/16/48 kHz.
4. Write a 4-step checklist to convert a 48 kHz mono Float32 track to a 16 kHz model input safely.
5. Why does \(\omega=\pi\) mean different Hz at different \(f_s\)?

## Further reading

- Oppenheim & Schafer — sampling theorem and multirate chapters.
- Standard DSP notes on decimation/interpolation.
- Web Audio API AudioContext `sampleRate` behavior; WebRTC getUserMedia constraints docs.
