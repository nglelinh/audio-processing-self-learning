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

![A spectrum copied at every sample rate, with copies overlapping when the signal is too wide]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Figure. Sampling repeats the spectrum every \(f_s\) hertz; overlap of those copies is aliasing, and it is not undone by a neural suppressor.*

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

The identity you will use in the lab is one line of the replica sum. On the sample grid \(t=n/f_s\),

$$
\cos\!\left(2\pi\frac{f}{f_s}n\right)
=\cos\!\left(2\pi\frac{f-mf_s}{f_s}n\right)
$$

because \(2\pi m n\) is an integer number of turns. Fold the representative into \([0,f_s/2]\) by reflecting at Nyquist if needed. For a 7 kHz cosine sampled at 8 kHz, take \(m=1\): \(|7000-8000|=1000\,\mathrm{Hz}\). The 7 kHz cosine and the 1 kHz cosine are the same sequence. A sine picks up a minus sign, \(\sin(2\pi\cdot 7n/8)=-\sin(2\pi\cdot 1n/8)\), because sine is odd under that full-turn shift. “Matches” means identical samples, not “sounds close.”

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

Speech intelligibility energy is not uniform: vowels live lower; consonants need highs. 8 kHz shreds many fricatives. 16 kHz is a common **model native** rate. 48 kHz often matches **device** graphs, and it is the full-band default of npm `deepfilternet3-noise-filter` 1.3.0, where Nyquist is 24 kHz. Your job is to resample **deliberately** between them. Feeding 48 kHz PCM to a 16 kHz STFT does not “give the net more resolution.” It assigns the wrong Hertz label to every bin and, without a low-pass near 8 kHz, folds 8–24 kHz energy into the band the model was trained to interpret as speech.

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

## Mini-lab

**Goal.** Sample a 7 kHz cosine at 8 kHz and show it is the same sequence as a 1 kHz cosine.

```python
import numpy as np

fs = 8000
n = np.arange(32)
high = np.cos(2 * np.pi * 7000 * n / fs)
low = np.cos(2 * np.pi * 1000 * n / fs)
err = np.max(np.abs(high - low))
print(f"{err:.3e}")
print(np.round(high[:8], 6).tolist())
```

**Expected.** An error below `1e-12` (typically about `1.354e-14`). The first eight samples round to `[1.0, 0.707107, -0.0, -0.707107, -1.0, -0.707107, -0.0, 0.707107]`.

**Failure modes.** Comparing sines and expecting a zero error without the sign flip. Declaring “no alias” because both arrays are float64. Low-pass filtering *after* the 8 kHz sampler and hoping the 7 kHz tone returns.

## Mini exercises

1. Nyquist frequency at 48 kHz and 16 kHz?
2. Alias of 10 kHz tone when \(f_s=16\,\mathrm{kHz}\) (express in \([0,f_s/2]\)).
3. Samples in 10 ms at 8/16/48 kHz.
4. Write a 4-step checklist to convert a 48 kHz mono Float32 track to a 16 kHz model input safely.
5. Why does \(\omega=\pi\) mean different Hz at different \(f_s\)?

### Answer hints

1. Nyquist frequency is \(f_s/2\): 24 kHz at 48 kHz, 8 kHz at 16 kHz.
2. \(10\,\mathrm{kHz}\) at \(16\,\mathrm{kHz}\) folds once: \(16-10=6\,\mathrm{kHz}\).
3. \(10\,\mathrm{ms}\) is 80, 160, and 480 samples.
4. Confirm 48 kHz mono float; low-pass near 8 kHz; decimate by 3; check a 1 kHz sine is still 1 kHz and that energy above 8 kHz is gone.
5. \(\omega=\pi\) is half a cycle per sample, which is \(f_s/2\) hertz. The digital frequency is normalized; the physical frequency is not.

## Further reading

- Oppenheim & Schafer — sampling theorem and multirate chapters.
- Julius O. Smith, *Mathematics of the DFT*, https://www.dsprelated.com/freebooks/mdft/ — sampling and the frequency axis used by an FFT.
- Web Audio API AudioContext `sampleRate` behavior; WebRTC getUserMedia constraints docs.
