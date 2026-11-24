---
layout: post
title: "01-07 Fourier pitfalls checklist for engineers"
chapter: "01"
order: 7
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

When a real-time noise suppressor sounds dull, metallic, or haunted, the reflex is almost always to blame the neural network and kick off a three-day retraining run. Nine times out of ten, the model weights are completely innocent—the culprit is an off-by-one Nyquist bin, a broken COLA window sum, swapped real/imaginary channels, or a silent 44.1 kHz vs. 48 kHz rate mismatch.

This capstone lesson of Chapter 01 distills every Fourier and STFT failure mode into a **10-point pre-flight engineering checklist** and a set of 5-line unit tests—so you always verify DSP hygiene first and touch model weights last.

![Sampling copies of a spectrum, the picture behind a mis-labeled Nyquist bin]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Figure. The dominant pitfall in this lesson is a wrong frequency axis: Nyquist is $$f_s/2$$, and an off-by-one bin is a different Hertz value, not a rounding error.*

**Lesson roadmap:** Background Knowledge Map (the three categories of silent DSP bugs: axis, energy/window, and symmetry/layout) → 10-point master pre-flight checklist → Worked debugging walk-throughs: off-by-one Nyquist bin ($$7968.75\,\mathrm{Hz}$$ vs. $$8000\,\mathrm{Hz}$$), swapped real/imag Hermitian violation, and 100 Hz COLA warble → Deep-Dive Explanation (Read Slowly): 3-step isolation protocol before touching neural weights → Unit tests, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: Why Fourier Bugs Fail Silently in Production

### 1. Axis & Rate Bugs (Right Math, Wrong Units)
An FFT array carries no sample-rate tag. Confusing bin $$N/2 - 1$$ with Nyquist $$N/2$$, labeling plots in raw bins instead of Hertz ($$f_k = k f_s / N$$), or feeding 48 kHz audio into a 16 kHz STFT produces zero runtime errors—yet shifts every spectral feature to the wrong physical frequency.

### 2. Energy, Window, and COLA Bugs
Double-dividing by $$N$$ on the inverse FFT drains audio amplitude; breaking the Constant Overlap-Add (COLA) condition imprints an audible tremolo at the hop frequency ($$f_{\text{warble}} = 1 / T_{\mathrm{hop}}$$); and mixing $$10\log_{10}$$ power dB with $$20\log_{10}$$ amplitude dB misleads every QA dashboard.

### 3. Symmetry & Memory-Layout Bugs
Real PCM requires a **Hermitian-symmetric** spectrum ($$X[k] = X^*[(N-k)\bmod N]$$ with purely real DC and Nyquist bins). Swapping real/imaginary parts or feeding interleaved stereo (`LRLR...`) into a mono FFT destroys phase coherence and injects phantom high-frequency energy.

---

## Learning objectives

1. Diagnose common FT/DFT mistakes in audio pipelines.
2. Validate units (Hz vs bin vs normalized frequency).
3. Apply a structured pre-flight checklist before blaming the neural model.
4. Recognize window/COLA and conjugate-symmetry failures by ear and by test.
5. Tie checklist items to Mezon / DeepFilterNet-style debugging without inventing internals.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–8 | War story format: symptom → wrong root cause → actual bug |
| 8–30 | Walk the master checklist with demos/thought experiments |
| 30–45 | Unit tests you should keep in repo |
| 45–55 | Mezon/DeepFilterNet debugging order |
| 55–60 | Exercises |

## Core explanations — master checklist

### 1) Sample rate truth

- [ ] PCM rate equals model rate (or documented resampler in between).
- [ ] Anti-alias filter present on downsampling.
- [ ] `AudioContext.sampleRate` not assumed 48 kHz on all devices.

**Symptom of failure:** robotic pitch shifts, dull audio, mysterious noise textures.

**Walk-through: the Nyquist bin is an integer, and it knows $$f_s$$.** For an even length $$N$$, the Nyquist bin is $$k=N/2$$, at

$$
f_{\mathrm{Nyquist}}=\frac{N/2}{N}f_s=\frac{f_s}{2}.
$$

Take $$N=512$$ and $$f_s=16\,\mathrm{kHz}$$. The true bin is $$k=256$$ at $$8000\,\mathrm{Hz}$$. The off-by-one index $$k=255$$ sits at $$255\times 16000/512=7968.75\,\mathrm{Hz}$$. A mask aimed at “the last speech bin” using 255 never touches Nyquist, and a test that only checks “some high bin moved” will pass. The same index at the product default of 48 kHz is $$256\times 48000/512=24000\,\mathrm{Hz}$$ if you forgot you were still on a 16 kHz array: you believe you are editing near 24 kHz while the samples only contain energy up to 8 kHz. `setSuppressionLevel(0–100)` then changes depth on the wrong axis. Fix the rate and the bin map before you touch `DeepFilterNet3Core`.

**Walk-through: swapped real and imaginary parts.** A real PCM frame has a conjugate-symmetric DFT, $$X[k]=X^*[(N-k)\bmod N]$$, and the Nyquist and DC bins are real. Swap real and imaginary parts and that identity fails by an amount on the order of the spectrum itself. The inverse transform grows a nonzero imaginary part that a “take the real part and move on” cast will hide as a dull, phasey residue. The mini-lab asserts both traps.

### 2) Units on the frequency axis

- [ ] Bin $$k$$ converted with $$f=k f_s/N$$.
- [ ] Filters specified in Hz converted using actual $$f_s$$.
- [ ] Plots labeled Hz, not raw bin indices, in QA reports.

### 3) FFT normalization / Parseval

- [ ] Forward/inverse scaling matches library docs.
- [ ] Round-trip STFT→ISTFT on impulse/random noise preserves energy (±window gain).
- [ ] Training and inference use the same norm.

**Symptom:** output gain pumping; metrics disagree with listening.

### 4) Window & COLA

- [ ] Analysis window documented.
- [ ] Synthesis window + hop satisfy COLA (constant overlap-add) for perfect reconstruction when $$\hat{X}=X$$.
- [ ] Same windows as training for neural front-ends.

**Symptom:** amplitude modulation at hop rate (tremolo), metallic warble.

### 5) Conjugate symmetry / packing

- [ ] Real iFFT inputs Hermitian.
- [ ] Nyquist/DC imaginary parts ~0.
- [ ] Packed real-FFT formats decoded correctly.

**Symptom:** imag leftovers, subtle distortion, framework errors.

### 6) Channel layout

- [ ] Interleaved vs planar agreed.
- [ ] Stereo → mono policy (mean / left / HRIR — pick one).
- [ ] Output channels match sink expectations.

### 7) Hop / latency accounting

- [ ] Look-ahead documented in ms.
- [ ] Ring buffer latency included in UX budget.
- [ ] Warmup frames discarded consistently in metrics.

### 8) DC and low-frequency junk

- [ ] DC blocker / high-pass if mic bias present.
- [ ] Not confusing DC with “noise” the model should remove.

### 9) dB displays

- [ ] $$20\log_{10}\vert X\vert$$ vs $$10\log_{10}\vert X\vert^2$$ consistency.
- [ ] Floor clamps to avoid $$\log 0$$.

### 10) Resampler + model domain

- [ ] Eval metrics at agreed rate.
- [ ] No double resampling in A/B tools.

## Worked debugging scenarios

### Warble at 100 Hz

Hop 10 ms → 100 hops/s. If COLA broken, amplitude modulates near 100 Hz. Fix windows/hop before touching weights.

### “Model muted fricatives”

Confirm input actually has energy >6 kHz (rate might be 8 kHz). Confirm mask not low-passing due to wrong bin mapping at 48 vs 16 kHz.

### SI-SDR great, users hate it

Phase/complex issues or musical noise; check symmetry and time-domain artifacts; run listening (Ch. 08).

---

### Deep-Dive Explanation: The 3-Step Isolation Protocol Before Touching Model Weights (Read Slowly)

#### Step 1: Run a deterministic sine & impulse round-trip with the neural model bypassed
Feed a pure 1 kHz sine and a unit impulse through your exact PCM $$\to$$ STFT $$\to$$ ISTFT $$\to$$ PCM wrapper with gain $$G \equiv 1$$. Check three assertions: (a) peak stays at exactly 1 kHz (verifies $$f_s$$ and channel stride), (b) output RMS matches input RMS to $$10^{-6}$$ (verifies Parseval & COLA), and (c) imaginary residue after iFFT is $$< 10^{-12}$$ (verifies Hermitian symmetry).

#### Step 2: Check boundary bins explicitly (DC $$k=0$$ and Nyquist $$k=N/2$$)
Off-by-one indexing bugs almost always hide at the two endpoints. Verify that `len(rfft_bins) == N // 2 + 1`, that `bin[0]` is DC ($$0\,\mathrm{Hz}$$), and that `bin[N // 2]` maps to $$f_s / 2$$—not `N // 2 - 1`.

#### Step 3: Change only ONE variable per experiment
Once the pass-through test is green, enable the neural model and inspect p99 callback time and listening samples. Never change sample rate, hop size, and checkpoint simultaneously—or you will never know which edit fixed (or broke) the call.

Summary of the pre-flight isolation order:

$$
\text{PCM rate \& layout}
\;\xrightarrow{\text{Bypass NS}}\;
\text{STFT}\to\text{ISTFT (COLA + Parseval + Hermitian)}
\;\xrightarrow{\text{All green}}\;
\text{Swap / tune neural model}.
$$

## Unit tests to keep

1. Impulse round-trip STFT/ISTFT (COLA).
2. Parseval check on FFT wrapper.
3. Hermitian projection test after random mask (optional).
4. Resampler sine: 1 kHz in → 1 kHz out, no alias spur.
5. Mono downmix length/channel asserts.

## Mezon / DeepFilterNet debugging order (public)

1. Verify PCM rate/channels against package README / model card.
2. Verify frame delivery (callbacks, ring buffer) — Ch. 05 themes.
3. Verify STFT hygiene (this checklist).
4. Only then swap model variants / strengths / npm options.
5. Cite public DeepFilterNet papers for expected algorithmic behavior; do not claim unpublished Mezon graph details.

## Common pitfalls

1. Changing three things at once (rate, hop, model).
2. Trusting a single café demo.
3. Using offline non-causal checkpoint in a streaming wrapper accidentally.
4. Ignoring p99 hop times.
5. “Fixing” warble with more aggressive NS gain.

## Mini-lab

**Goal.** Fail an assert on a swapped real/imaginary spectrum, and show an off-by-one Nyquist bin is not 8 kHz.

```python
import numpy as np

def hermitian_error(X):
    n = np.arange(X.shape[0])
    mirror = np.conj(X[(X.shape[0] - n) % X.shape[0]])
    return np.max(np.abs(X - mirror))

x = np.array([1.0, 0.5, -0.2, 0.1, 0.0, -0.3, 0.4, 0.2])
X = np.fft.fft(x)
swapped = X.imag + 1j * X.real

def nyquist_hz(n_fft, fs):
    return (n_fft // 2) * fs / n_fft

print(f"good={hermitian_error(X):.3e}")
print(f"swapped={hermitian_error(swapped):.3f}")
print(f"nyquist={nyquist_hz(512, 16000):.2f}")
print(f"off_by_one={(512 // 2 - 1) * 16000 / 512:.2f}")
assert hermitian_error(X) < 1e-8
assert hermitian_error(swapped) > 1e-3
assert nyquist_hz(512, 16000) == 8000.0
```

**Expected.** `good=0.000e+00`, `swapped=3.400`, `nyquist=8000.00`, `off_by_one=7968.75`. The three asserts pass. Delete the swap assert and a broken spectrum ships; point `nyquist_hz` at `N/2-1` and the last assert fires.

**Failure modes.** Checking symmetry with `np.allclose(X, np.conj(X[::-1]))` and forgetting that index 0 must match itself, not a reversed neighbor (the formula above uses $$(N-k)\bmod N$$, so DC maps to DC). Treating 7968.75 Hz as “close enough to Nyquist” for a unit test.

## Mini exercises

1. Pick three checklist items and write a unit test name for each.
2. Hop 5 ms warble frequency if COLA fails?
3. Why does wrong $$f_s$$ in $$f=kf_s/N$$ mimic a bad model?
4. Draft a 6-step incident report template for “NS sounds bad in Chrome.”
5. Which checklist item catches interleaved stereo fed to a mono FFT?

### Answer hints

1. Name tests after the failure: `test_cola_impulse_roundtrip`, `test_parseval_scale`, `test_downmix_length`.
2. A broken COLA at a 5 ms hop modulates near $$1/0.005=200\,\mathrm{Hz}$$.
3. Every bin label scales with $$f_s$$. A 16 kHz model fed 48 kHz numbers looks like a low-pass even when the weights are untouched.
4. Rate, channels, hop in ms, p95 callback time, one COLA impulse check, then the model id. One change per retry.
5. Channel layout: interleaved stereo read as mono alternates left and right into consecutive “time” samples.

## Further reading

- Oppenheim & Schafer — windows, scaling, DFT pitfalls chapters.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — configuration and real-time notes. Julius O. Smith, https://ccrma.stanford.edu/~jos/mdft/, for the DFT symmetries the asserts check.
- ORT / browser profiling docs (high level) for separating STFT vs net costs.

## Video tham khảo

- [11: Spectral Analysis Part 1 - Intro to Neural Computation](https://www.youtube.com/watch?v=4ip-4ai6kN8) — MIT OpenCourseWare, English. **xem trước.** The lecture's point is that calling an FFT is easy to do wrong. Watch the axis, scaling, and window warnings before you retrain a model.
- [Lecture 13: Spectral Leakage, Windowing, with Examples of Hanning and Hamming Windows](https://www.youtube.com/watch?v=tCWU9C-LdJQ) — Bahga Lab IIT Delhi, English. Hann versus rectangular sidelobes are the leakage half of the checklist.
- [Xiph.Org Video Presentations: Digital Show & Tell](https://xiph.org/video/vid2.shtml) — Xiph.Org, English. Official Xiph.Org presentation of sampling and reconstruction. Use it when a frequency axis is wrong because the rate, not the network, moved.
