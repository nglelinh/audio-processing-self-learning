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

The short-time Fourier transform is the workhorse for classical NS and for DeepFilterNet-class models. The forward transform below uses one analysis window; the inverse names the synthesis window separately, so the COLA condition from lesson 02-02 applies without a hidden second multiply.

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

![The same overlap-add picture as framing: analysis frames, Hann windows stepping by hop R, and the window sum that ISTFT relies on]({{ site.imgurl }}/generated/stft-ola.png)

*Figure. Each colored frame is one STFT column; ISTFT overlap-adds the inverse frames, and the bottom sum must be constant or the sine wave on top comes back with a hop-rate envelope.*

## Core explanations

### STFT

$$
X(\ell,k)=\sum_{n=0}^{L-1}x[n+\ell R]\,w[n]\,e^{-j2\pi kn/N}
$$

Here \(w[n]\) is the **analysis** window \(w_{\mathrm{ana}}\). Grid: columns = time frames \(\ell\), rows = frequency bins \(k\). Speech enhancement estimates clean \(\hat{X}(\ell,k)\) from noisy \(Y(\ell,k)\).

\(N\) is the FFT length. It may exceed \(L\) when you zero-pad; smaller than \(L\) time-aliases the frame. Bin spacing is \(f_s/N\), but resolution is still the window (lesson 02-03). A real signal has \(N/2+1\) unique bins, Nyquist in the last.

### ISTFT

Inverse FFT per frame, optional synthesis window, then OLA. One frame of the inverse, before overlap-add, is

$$
y_\ell[n]=\frac{1}{N}\sum_{k=0}^{N-1}\hat{X}(\ell,k)\,e^{j2\pi kn/N},\qquad n=0,\ldots,L-1
$$

(with the usual real-FFT packing when you call `irfft`). The waveform is

$$
\hat{x}[n]=\sum_\ell w_{\mathrm{syn}}[n-\ell R]\,y_\ell[n-\ell R].
$$

If the forward transform already multiplied by \(w\) and \(w_{\mathrm{syn}}=1\), unmodified reconstruction reduces to \(\sum_\ell w[n-\ell R]=C\) and a divide by \(C\). If you also multiply by a synthesis window, COLA is the product sum from lesson 02-02:

$$
\sum_\ell w[n-\ell R]\,w_{\mathrm{syn}}[n-\ell R]=C.
$$

If no modification and COLA holds, reconstruct \(x\) (delay/gain aside). A centered offline STFT shifts by about \(L/2\) relative to a causal stream; both can be COLA and still disagree by enough delay to wreck SI-SDR.

### Representations

| Representation | Contents | Typical use |
|----------------|----------|-------------|
| Complex \(X\) | real/imag or mag/phase | deep filtering, complex masks |
| Magnitude \(|X\|\) | nonneg | classical Wiener, mag masks |
| Log-mag / dB | compressed | features, plots |
| ERB / Mel filterbanks | band energies | perceptual front-ends (DeepFilterNet uses ERB-scale features in papers) |

### Magnitude masks vs deep filtering (intuition)

**Magnitude mask:** \(\hat{X}=M\odot|Y|e^{j\arg Y}\) (reuse noisy phase). Cheap; phase errors on low SNR.

**Complex mask / filtering:** predict filters that mix neighboring time-frequency bins — **deep filtering** in DeepFilterNet literature applies learned filters on complex spectra to better recover structure than independent per-bin gains.

Read DeepFilterNet / DeepFilterNet2 / DeepFilterNet3 papers for the precise architecture; this lesson only needs the engineering moral: **you are modifying an STFT grid under causal constraints**, then ISTFT-ing back.

### Perfect reconstruction practice

Unit test: STFT→ISTFT without model ≈ identity. Then enable the model. If identity already fails, stop. The mini-lab is that test on a sine: float64 error around \(10^{-15}\) in the interior. An error of \(10^{-2}\) is a window or hop bug and becomes a hop-rate tremolo.

### Parameter mapping

Extract from docs/papers:

- \(f_s\)
- window type & \(L\) / FFT \(N\)
- hop \(R\)
- causal look-ahead
- mono assumption

Translate to ms and hops/s using Ch. 01–02 formulas before integration testing with `deepfilternet3-noise-filter` or ORT.

**Published DeepFilterNet grid.** The framework is specified for rates up to 48 kHz, and the reported full-band setup uses \(N_{\mathrm{FFT}}=960\) (20 ms at 48 kHz) with 50% overlap, so \(R=480\) (10 ms). See Schröter et al., [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), and the reference configuration in [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (`sr=48000`, `fft_size=960`, `hop_size=480`). The window is part of that checkpoint: whatever analysis/synthesis pair the library applies, hop and window must match the model. The npm package `deepfilternet3-noise-filter` 1.3.0 follows the same 48 kHz full-band contract. Swapping in a 16 kHz hop, a Blackman window, or a centered offline STFT does not “improve quality”; it feeds the ERB filterbank a different grid than the weights expect.

That setup also reports a small convolutional look-ahead (\(l_{\mathrm{DNN}}=2\) frames and \(l_{\mathrm{DF}}=1\) frame). At a 10 ms hop those frames sit on top of the 20 ms window. Copy them from the checkpoint.

## Worked examples

### Grid shape

1 s @ 16 kHz, \(R=256\), \(N=512\) real FFT → about \(16000/256\approx 62\) frames (edge policy can change this by one), 257 unique bins (0..Nyquist). A mask tensor might be \([1,257,62]\) or channels-first variants — match the model.

2 s @ 48 kHz, \(R=480\), \(N=960\): frames \(\approx 96000/480=200\), unique bins \(960/2+1=481\). That is the shape family a 48 kHz DeepFilterNet integration has to allocate, not 257 bins.

### Phase reuse limit

Low-SNR bin: noisy phase ≈ random. Magnitude mask cleans energy but residual sounds watery. Complex methods try harder — still not magic under babble.

## Common pitfalls

1. Centering frames offline but not in streaming (alignment skew).
2. Training with different hop than serving.
3. Feeding Mel features into a model that expects ERB or linear STFT.
4. Batch ISTFT on whole files in prod (latency).
5. Claiming undocumented Mezon STFT constants from this course.

## Mini-lab

**Goal.** Round-trip a 440 Hz sine through an analysis-window STFT and an overlap-add ISTFT, and print the max absolute error in the interior.

```python
import numpy as np

fs, L, R = 16000, 256, 128
w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(L) / L)
t = np.arange(fs) / fs
x = 0.5 * np.sin(2 * np.pi * 440 * t)
starts = range(0, len(x) - L + 1, R)
specs = [np.fft.rfft(x[s:s + L] * w) for s in starts]
y = np.zeros_like(x)
acc = np.zeros_like(x)
for s, spec in zip(starts, specs):
    y[s:s + L] += np.fft.irfft(spec, n=L)  # analysis window already in the frame
    acc[s:s + L] += w
mid = slice(L, len(x) - L)
err = np.max(np.abs(y[mid] / acc[mid] - x[mid]))
print("max abs error", err)
```

**Expected.** `max abs error` on the order of \(10^{-15}\) (float64 roundoff). The COLA divisor `acc` is the constant 1 in the interior, as in lesson 02-02.

**Failure modes.** Omitting the divide by `acc` leaves a half-scale or rippling output and an error near \(10^{-1}\). Using a symmetric Hann, or applying `w` again on the inverse frame, produces a hop-periodic error large enough to hear. Scoring the first `L` samples, where `acc` has not reached the constant, inflates the error even when the steady region is perfect. A non-zero error with this exact script means the FFT backend is not round-tripping, not that COLA is optional.

## Mini exercises

1. Write STFT shapes for 2 s audio @ 48 kHz, \(R=480\), \(N=960\) (approx frames).
2. Why reuse noisy phase fails in deep noise?
3. List four parameters to copy from a DeepFilterNet config into your integrator checklist.
4. What does COLA failure sound like after ISTFT?
5. ERB vs linear STFT: one reason for ERB in speech enhancement front-ends?

### Answer hints

1. About 200 frames and 481 real bins.
2. At low SNR the noisy phase is close to the noise’s phase, so a perfect magnitude still modulates the speech.
3. \(f_s\), FFT length, hop, window (and any stated look-ahead). The public defaults to check are 48 kHz, 960, 480.
4. Amplitude tremolo at \(f_s/R\) (100 Hz for a 10 ms hop).
5. ERB spends bins where the ear (and speech formants) have resolution, instead of uniform hertz.

## Further reading

- DeepFilterNet, DeepFilterNet2, DeepFilterNet3 papers — STFT, ERB, deep filtering sections. Start at [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) and the reference code [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Julius O. Smith, *Spectral Audio Signal Processing* — STFT and ISTFT definitions consistent with the windows.
- Oppenheim & Schafer — filter banks / STFT connections.
