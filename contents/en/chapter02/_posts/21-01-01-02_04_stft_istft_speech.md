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

Every piece we built in Lessons 02-01 through 02-03—PCM scaling, overlapping frames, periodic Hann windows, and COLA—now clicks together into the single most important transform in speech enhancement: the **Short-Time Fourier Transform (STFT)** and its inverse (**ISTFT**).

Whether you run classical Wiener filtering or **DeepFilterNet3** at 48 kHz full-band, your enhancer lives on a 2D complex time–frequency grid $$X(\ell, k)$$. This lesson makes the STFT/ISTFT contract exact, contrasts simple magnitude masking with complex deep filtering, and maps the published DeepFilterNet grid ($$f_s = 48\,\mathrm{kHz}$$, $$N_{\mathrm{FFT}} = 960$$, $$R = 480$$) onto real tensor shapes.

![The same overlap-add picture as framing: analysis frames, Hann windows stepping by hop R, and the window sum that ISTFT relies on]({{ site.imgurl }}/generated/stft-ola.png)

*Figure. Each colored frame is one STFT column; ISTFT overlap-adds the inverse frames, and the bottom sum must be constant or the sine wave on top comes back with a hop-rate envelope.*

**Lesson roadmap:** Key ideas (the STFT time–frequency grid, magnitude masks vs. complex deep filtering, offline centered vs. causal streaming STFT) → Forward STFT & Inverse ISTFT equations → Published DeepFilterNet 48 kHz grid → Worked examples: computing exact tensor shapes for 16 kHz / 512 and 48 kHz / 960 (481 bins) and phase-reuse limits → Explanation: 3 steps verifying perfect reconstruction before adding a model → Pitfalls, Mini-lab, Exercises & Videos.

---

## Key ideas: Time–Frequency Grids and Speech Enhancement Front-Ends

### 1. The STFT as a 2D Complex Matrix $$X(\ell, k)$$
Sliding a length-$$L$$ analysis window across a waveform in steps of $$R$$ and taking an $$N$$-point `rfft` produces a complex matrix of shape $$[N/2 + 1,\; T_{\text{frames}}]$$. Each column $$\ell$$ is a snapshot of the local spectrum; each row $$k$$ tracks how one frequency bin evolves over time.

### 2. Magnitude Masks vs. Complex Deep Filtering
- **Magnitude masking** multiplies $$\vert Y(\ell, k)\vert$$ by a real gain $$M(\ell, k) \in [0, 1]$$ and reuses the noisy phase $$\arg Y$$. It is cheap, but at low SNR the noisy phase is corrupted, leaving speech sounding watery.
- **Complex deep filtering** (used by DeepFilterNet) predicts small complex FIR filters across neighboring time frames for each frequency bin—jointly refining both magnitude *and* phase!

### 3. Centered Offline STFT vs. Causal Streaming STFT
Libraries like PyTorch `torch.stft(..., center=True)` pad $$L/2$$ samples on the left, shifting every frame by $$L/2$$ relative to a causal streaming STFT. Both satisfy COLA individually, yet mixing a centered training STFT with a causal serving STFT silently shifts alignment and degrades SI-SDR.

---

## Learning objectives

1. Build a mental model of the STFT grid (time × frequency).
2. Contrast magnitude masks, complex masks, and deep filtering ideas.
3. State practical perfect-reconstruction conditions.
4. Map STFT parameters (rate, $$N$$, hop, window) to latency and resolution.
5. Connect DeepFilterNet’s published STFT-centric design to engineering parameters.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | STFT definition; spectrogram as $$\vert\text{STFT}\vert$$ |
| 12–28 | ISTFT / OLA; perfect reconstruction drills |
| 28–42 | Mag vs complex processing; deep filtering intuition |
| 42–52 | DeepFilterNet paper parameter extraction exercise |
| 52–60 | Exercises |

## Core explanations

### STFT

$$
X(\ell,k)=\sum_{n=0}^{L-1}x[n+\ell R]\,w[n]\,e^{-j2\pi kn/N}
$$

Here $$w[n]$$ is the **analysis** window $$w_{\mathrm{ana}}$$. Grid: columns = time frames $$\ell$$, rows = frequency bins $$k$$. Speech enhancement estimates clean $$\hat{X}(\ell,k)$$ from noisy $$Y(\ell,k)$$.

$$N$$ is the FFT length. It may exceed $$L$$ when you zero-pad; smaller than $$L$$ time-aliases the frame. Bin spacing is $$f_s/N$$, but resolution is still the window (lesson 02-03). A real signal has $$N/2+1$$ unique bins, Nyquist in the last.

### ISTFT

Inverse FFT per frame, optional synthesis window, then OLA. One frame of the inverse, before overlap-add, is

$$
y_\ell[n]=\frac{1}{N}\sum_{k=0}^{N-1}\hat{X}(\ell,k)\,e^{j2\pi kn/N},\qquad n=0,\ldots,L-1
$$

(with the usual real-FFT packing when you call `irfft`). The waveform is

$$
\hat{x}[n]=\sum_\ell w_{\mathrm{syn}}[n-\ell R]\,y_\ell[n-\ell R].
$$

If the forward transform already multiplied by $$w$$ and $$w_{\mathrm{syn}}=1$$, unmodified reconstruction reduces to $$\sum_\ell w[n-\ell R]=C$$ and a divide by $$C$$. If you also multiply by a synthesis window, COLA is the product sum from lesson 02-02:

$$
\sum_\ell w[n-\ell R]\,w_{\mathrm{syn}}[n-\ell R]=C.
$$

If no modification and COLA holds, reconstruct $$x$$ (delay/gain aside). A centered offline STFT shifts by about $$L/2$$ relative to a causal stream; both can be COLA and still disagree by enough delay to wreck SI-SDR.

### Representations

| Representation | Contents | Typical use |
|----------------|----------|-------------|
| Complex $$X$$ | real/imag or mag/phase | deep filtering, complex masks |
| Magnitude $$\vert X\vert$$ | nonneg | classical Wiener, mag masks |
| Log-mag / dB | compressed | features, plots |
| ERB / Mel filterbanks | band energies | perceptual front-ends (DeepFilterNet uses ERB-scale features in papers) |

### Magnitude masks vs deep filtering (intuition)

**Magnitude mask:** $$\hat{X}=M\odot\vert Y\vert e^{j\arg Y}$$ (reuse noisy phase). Cheap; phase errors on low SNR.

**Complex mask / filtering:** predict filters that mix neighboring time-frequency bins — **deep filtering** in DeepFilterNet literature applies learned filters on complex spectra to better recover structure than independent per-bin gains.

Read DeepFilterNet / DeepFilterNet2 / DeepFilterNet3 papers for the precise architecture; this lesson only needs the engineering moral: **you are modifying an STFT grid under causal constraints**, then ISTFT-ing back.

### Perfect reconstruction practice

Unit test: STFT→ISTFT without model ≈ identity. Then enable the model. If identity already fails, stop. The mini-lab is that test on a sine: float64 error around $$10^{-15}$$ in the interior. An error of $$10^{-2}$$ is a window or hop bug and becomes a hop-rate tremolo.

### Parameter mapping

Extract from docs/papers:

- $$f_s$$
- window type & $$L$$ / FFT $$N$$
- hop $$R$$
- causal look-ahead
- mono assumption

Translate to ms and hops/s using Ch. 01–02 formulas before integration testing with `deepfilternet3-noise-filter` or ORT.

**Published DeepFilterNet grid.** The framework is specified for rates up to 48 kHz, and the reported full-band setup uses $$N_{\mathrm{FFT}}=960$$ (20 ms at 48 kHz) with 50% overlap, so $$R=480$$ (10 ms). See Schröter et al., [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), and the reference configuration in [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (`sr=48000`, `fft_size=960`, `hop_size=480`). The window is part of that checkpoint: whatever analysis/synthesis pair the library applies, hop and window must match the model. The npm package `deepfilternet3-noise-filter` 1.3.0 follows the same 48 kHz full-band contract. Swapping in a 16 kHz hop, a Blackman window, or a centered offline STFT does not “improve quality”; it feeds the ERB filterbank a different grid than the weights expect.

That setup also reports a small convolutional look-ahead ($$l_{\mathrm{DNN}}=2$$ frames and $$l_{\mathrm{DF}}=1$$ frame). At a 10 ms hop those frames sit on top of the 20 ms window. Copy them from the checkpoint.

## Worked examples

### Grid shape

1 s @ 16 kHz, $$R=256$$, $$N=512$$ real FFT → about $$16000/256\approx 62$$ frames (edge policy can change this by one), 257 unique bins (0..Nyquist). A mask tensor might be $$[1,257,62]$$ or channels-first variants — match the model.

2 s @ 48 kHz, $$R=480$$, $$N=960$$: frames $$\approx 96000/480=200$$, unique bins $$960/2+1=481$$. That is the shape family a 48 kHz DeepFilterNet integration has to allocate, not 257 bins.

### Phase reuse limit

Low-SNR bin: noisy phase ≈ random. Magnitude mask cleans energy but residual sounds watery. Complex methods try harder — still not magic under babble.

---

### Explanation: The 3-Step STFT/ISTFT Contract for Neural Speech Enhancement

#### Step 1: Lock the five grid numbers from the model card
Before writing a single line of inference code, copy $$(f_s,\; L,\; N,\; R,\; w_{\mathrm{ana}}/w_{\mathrm{syn}})$$ verbatim from the training config. For DeepFilterNet full-band: $$f_s = 48{,}000$$, $$L = N = 960$$, $$R = 480$$, giving $$481$$ real-FFT bins spaced by $$50\,\mathrm{Hz}$$ and $$100$$ frames per second.

#### Step 2: Verify bit-level round-trip identity in the steady interior
Run a pure sine wave through your streaming STFT $$\to$$ ISTFT with no neural mask and check $$\max \vert \hat{x}[n] - x[n]\vert$$ for $$n \in [L,\; N_{\text{tot}} - L]$$. Float64 error must be $$\sim 10^{-15}$$ (float32 $$\sim 10^{-6}$$). Anything around $$10^{-2}$$ means your window or COLA divisor is broken.

#### Step 3: Understand why ISTFT after masking is a *projection*, not always an exact STFT
When a suppressor modifies $$Y(\ell, k) \mapsto \hat{X}(\ell, k)$$, adjacent modified frames may no longer be 100% mutually consistent in the time domain. Overlap-add acts as a **least-squares projection** back onto a consistent waveform—which is why smooth complex masks (or DeepFilterNet’s multi-frame complex filters) synthesize far cleaner speech than jagged per-bin magnitude gates!

Summary of the STFT enhancement pipeline:

$$
x[n]
\;\xrightarrow{\text{Window } w_{\mathrm{ana}} + \text{rfft}}\;
Y(\ell, k) \in \mathbb{C}^{481 \times T}
\;\xrightarrow{\text{ERB + Deep Filtering}}\;
\hat{X}(\ell, k)
\;\xrightarrow{\text{irfft} + \text{COLA OLA}}\;
\hat{x}[n].
$$

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

**Expected.** `max abs error` on the order of $$10^{-15}$$ (float64 roundoff). The COLA divisor `acc` is the constant 1 in the interior, as in lesson 02-02.

**Failure modes.** Omitting the divide by `acc` leaves a half-scale or rippling output and an error near $$10^{-1}$$. Using a symmetric Hann, or applying `w` again on the inverse frame, produces a hop-periodic error large enough to hear. Scoring the first `L` samples, where `acc` has not reached the constant, inflates the error even when the steady region is perfect. A non-zero error with this exact script means the FFT backend is not round-tripping, not that COLA is optional.

## Mini exercises

1. Write STFT shapes for 2 s audio @ 48 kHz, $$R=480$$, $$N=960$$ (approx frames).
2. Why reuse noisy phase fails in deep noise?
3. List four parameters to copy from a DeepFilterNet config into your integrator checklist.
4. What does COLA failure sound like after ISTFT?
5. ERB vs linear STFT: one reason for ERB in speech enhancement front-ends?

### Answer hints

1. About 200 frames and 481 real bins.
2. At low SNR the noisy phase is close to the noise’s phase, so a perfect magnitude still modulates the speech.
3. $$f_s$$, FFT length, hop, window (and any stated look-ahead). The public defaults to check are 48 kHz, 960, 480.
4. Amplitude tremolo at $$f_s/R$$ (100 Hz for a 10 ms hop).
5. ERB spends bins where the ear (and speech formants) have resolution, instead of uniform hertz.

## Further reading

- DeepFilterNet, DeepFilterNet2, DeepFilterNet3 papers — STFT, ERB, deep filtering sections. Start at [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) and the reference code [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Julius O. Smith, *Spectral Audio Signal Processing* — STFT and ISTFT definitions consistent with the windows.
- Oppenheim & Schafer — filter banks / STFT connections.

## Video tham khảo

- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, English. **xem trước.** Watch analysis frames and the idea that an inverse transform has to undo them. That pair is the STFT/ISTFT contract for speech.
- [The Spectrogram and the Gabor Transform](https://www.youtube.com/watch?v=EfWnEldTyPA) — Steve Brunton, English. A moving window on a Fourier transform is the spectrogram. Use it as the speech-time picture DeepFilterNet's front end assumes.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, English. Watch the STFT into ERB bands and the inverse STFT out. The lesson's DeepFilterNet tie-in is this block, not the training loss.
