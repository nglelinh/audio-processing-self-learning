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

When NS “sounds broken,” engineers often retrain models first. This lesson is a pre-flight Fourier/STFT checklist: units, windows, symmetry, scaling, resampling, and DC/Nyquist — so you blame the network last.

![Sampling copies of a spectrum, the picture behind a mis-labeled Nyquist bin]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Figure. The dominant pitfall in this lesson is a wrong frequency axis: Nyquist is \(f_s/2\), and an off-by-one bin is a different Hertz value, not a rounding error.*

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

**Walk-through: the Nyquist bin is an integer, and it knows \(f_s\).** For an even length \(N\), the Nyquist bin is \(k=N/2\), at

$$
f_{\mathrm{Nyquist}}=\frac{N/2}{N}f_s=\frac{f_s}{2}.
$$

Take \(N=512\) and \(f_s=16\,\mathrm{kHz}\). The true bin is \(k=256\) at \(8000\,\mathrm{Hz}\). The off-by-one index \(k=255\) sits at \(255\times 16000/512=7968.75\,\mathrm{Hz}\). A mask aimed at “the last speech bin” using 255 never touches Nyquist, and a test that only checks “some high bin moved” will pass. The same index at the product default of 48 kHz is \(256\times 48000/512=24000\,\mathrm{Hz}\) if you forgot you were still on a 16 kHz array: you believe you are editing near 24 kHz while the samples only contain energy up to 8 kHz. `setSuppressionLevel(0–100)` then changes depth on the wrong axis. Fix the rate and the bin map before you touch `DeepFilterNet3Core`.

**Walk-through: swapped real and imaginary parts.** A real PCM frame has a conjugate-symmetric DFT, \(X[k]=X^*[(N-k)\bmod N]\), and the Nyquist and DC bins are real. Swap real and imaginary parts and that identity fails by an amount on the order of the spectrum itself. The inverse transform grows a nonzero imaginary part that a “take the real part and move on” cast will hide as a dull, phasey residue. The mini-lab asserts both traps.

### 2) Units on the frequency axis

- [ ] Bin \(k\) converted with \(f=k f_s/N\).
- [ ] Filters specified in Hz converted using actual \(f_s\).
- [ ] Plots labeled Hz, not raw bin indices, in QA reports.

### 3) FFT normalization / Parseval

- [ ] Forward/inverse scaling matches library docs.
- [ ] Round-trip STFT→ISTFT on impulse/random noise preserves energy (±window gain).
- [ ] Training and inference use the same norm.

**Symptom:** output gain pumping; metrics disagree with listening.

### 4) Window & COLA

- [ ] Analysis window documented.
- [ ] Synthesis window + hop satisfy COLA (constant overlap-add) for perfect reconstruction when \(\hat{X}=X\).
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

- [ ] \(20\log_{10}|X|\) vs \(10\log_{10}|X|^2\) consistency.
- [ ] Floor clamps to avoid \(\log 0\).

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

**Failure modes.** Checking symmetry with `np.allclose(X, np.conj(X[::-1]))` and forgetting that index 0 must match itself, not a reversed neighbor (the formula above uses \((N-k)\bmod N\), so DC maps to DC). Treating 7968.75 Hz as “close enough to Nyquist” for a unit test.

## Mini exercises

1. Pick three checklist items and write a unit test name for each.
2. Hop 5 ms warble frequency if COLA fails?
3. Why does wrong \(f_s\) in \(f=kf_s/N\) mimic a bad model?
4. Draft a 6-step incident report template for “NS sounds bad in Chrome.”
5. Which checklist item catches interleaved stereo fed to a mono FFT?

### Answer hints

1. Name tests after the failure: `test_cola_impulse_roundtrip`, `test_parseval_scale`, `test_downmix_length`.
2. A broken COLA at a 5 ms hop modulates near \(1/0.005=200\,\mathrm{Hz}\).
3. Every bin label scales with \(f_s\). A 16 kHz model fed 48 kHz numbers looks like a low-pass even when the weights are untouched.
4. Rate, channels, hop in ms, p95 callback time, one COLA impulse check, then the model id. One change per retry.
5. Channel layout: interleaved stereo read as mono alternates left and right into consecutive “time” samples.

## Further reading

- Oppenheim & Schafer — windows, scaling, DFT pitfalls chapters.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — configuration and real-time notes. Julius O. Smith, https://ccrma.stanford.edu/~jos/mdft/, for the DFT symmetries the asserts check.
- ORT / browser profiling docs (high level) for separating STFT vs net costs.
