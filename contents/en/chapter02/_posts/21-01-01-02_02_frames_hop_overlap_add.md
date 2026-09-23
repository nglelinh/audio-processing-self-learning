---
layout: post
title: "02-02 Frames, hop size, and overlap-add"
chapter: "02"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

STFT pipelines carve audio into overlapping frames, process each, and glue them with overlap-add (OLA). A bad hop or OLA produces warble that no weight update will fix. This lesson derives constant-overlap-add (COLA) for a periodic Hann and puts milliseconds on \(L\) and \(R\).

## Learning objectives

1. Define frame length \(L\), hop \(R\), and overlap ratio.
2. Explain overlap-add reconstruction and the COLA condition.
3. Compute algorithmic delay implications of \(L\) and \(R\).
4. Choose hops for speech NS with latency/quality intuition.
5. Implement a mental model of streaming OLA buffers.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Frame/hop diagrams on the whiteboard |
| 12–28 | OLA math; COLA with Hann examples |
| 28–42 | Streaming buffer mechanics; edge effects |
| 42–52 | Numerics at 16/48 kHz for speech |
| 52–60 | Exercises |

![Overlapping analysis frames, sliding Hann windows of length L and hop R, and their overlap-add sum]({{ site.imgurl }}/generated/stft-ola.png)

*Figure. Frames of length \(L\) advance by hop \(R\); overlap-add rebuilds the waveform only where the sum of the shifted windows is constant.*

## Core explanations

### Framing

Window length \(L\) samples; hop \(R\) samples (\(1\le R\le L\)). Overlap ratio:

$$
\rho = 1-\frac{R}{L}
$$

50% overlap means \(R=L/2\); 75% means \(R=L/4\). The hop is also the number of new samples you must collect before the next FFT, so

$$
T_R=\frac{R}{f_s},\qquad \text{hops/s}=\frac{f_s}{R},\qquad T_L=\frac{L}{f_s}.
$$

\(T_L\) is how much audio sits inside one analysis frame. \(T_R\) is how often you emit a new frame. They are not interchangeable: a 20 ms window with a 10 ms hop still looks at 20 ms of context every time it runs.

### Overlap-add

Given modified frames \(y_m[n]=w_{\mathrm{syn}}[n]\cdot \mathrm{iFFT}(\hat{X}_m)\), output:

$$
\hat{x}[n]=\sum_m y_m[n-mR]
$$

If \(\hat{X}_m\) equals analysis STFT of \(x\) and windows satisfy **COLA**, \(\hat{x}\) reconstructs \(x\) (up to delay/gain). The analysis step already multiplied by \(w_{\mathrm{ana}}\). Anything you multiply again after the iFFT is \(w_{\mathrm{syn}}\). Writing both down is how you avoid windowing twice.

### COLA (constant overlap-add)

For hop \(R\), analysis/synthesis windows must make the sum of shifted window products constant:

$$
\sum_m w_{\mathrm{ana}}[n-mR]\,w_{\mathrm{syn}}[n-mR] = C
$$

(Exact statement depends on whether windows are applied once or twice; be consistent with your STFT definition.) Hann with 50% overlap is a classic COLA choice when used carefully.

**Derivation for the periodic Hann.** Define

$$
w[n]=\frac12-\frac12\cos\frac{2\pi n}{L},\qquad n=0,\ldots,L-1.
$$

The denominator is \(L\), not \(L-1\). That is the *periodic* Hann (`sym=False` in NumPy). The symmetric Hann that forces \(w[0]=w[L-1]=0\) does **not** sum to a constant, and it is a common reason a “Hann 50%” unit test fails by a few thousandths.

Set \(R=L/2\) and consider an interior sample where two windows cover \(n\). Let \(\theta=2\pi n/L\). Then

$$
w[n]=\frac12(1-\cos\theta),\qquad
w[n+R]=\frac12\bigl(1-\cos(\theta+\pi)\bigr)=\frac12(1+\cos\theta).
$$

Add them:

$$
w[n]+w[n+R]=\frac12(1-\cos\theta)+\frac12(1+\cos\theta)=1.
$$

So if \(w_{\mathrm{ana}}=w\) and \(w_{\mathrm{syn}}=1\) on the frame (you do not window a second time), the COLA sum in the steady region is the constant \(C=1\). The mini-lab prints that constant.

**What is not constant.** The sum of *squares* of the same window is

$$
w[n]^2+w[n+R]^2=\frac12\bigl(1+\cos^2\theta\bigr),
$$

which ripples between \(1/2\) and \(1\). If you apply the full Hann on the way in and again on the way out, the product sum is this ripple, and the waveform pumps at \(f_s/R\) hertz. The usual repair is to split the window: \(w_{\mathrm{ana}}=w_{\mathrm{syn}}=\sqrt{w}\). Then the product is \(w\), and the sum of products is the constant we just proved. That is why \(\sqrt{\mathrm{Hann}}\) shows up in STFT code even though the COLA identity is about \(w\).

### Latency

Larger \(L\) → more frequency detail, more buffering delay. Smaller \(R\) → denser updates, higher CPU (more hops/s), often smoother masks. Product NS usually lives in the 5–20 ms hop ballpark for speech, but **match the model**.

For a causal streaming analysis window, the algorithmic delay is on the order of the window, not the hop:

$$
D_{\mathrm{alg}}\approx T_L=\frac{L}{f_s}.
$$

You cannot form the frame until its last sample has arrived. Shrinking \(R\) from \(L/2\) to \(L/4\) doubles hops/s but does not cut \(D_{\mathrm{alg}}\) in half. A centered STFT needs about \(T_L/2\) of look-ahead. Lesson 02-07 separates this delay from real-time factor.

### Streaming OLA buffer

Keep an output accumulator of length \(\ge L\). Each hop, add the new frame, emit the \(R\) samples no future frame will touch, and carry the tail. The first \(L-R\) samples are a partial sum, not the constant \(C\); fade them. Clearing the accumulator on every callback restarts that partial sum and *is* the tremolo.

## Worked examples

### Numbers

\(f_s=48\,\mathrm{kHz}\), \(L=960\) (20 ms), \(R=480\) (10 ms): \(\rho=0.5\), hops/s \(=48000/480=100\), \(D_{\mathrm{alg}}\approx 20\,\mathrm{ms}\). This is the public DeepFilterNet analysis grid: \(N_{\mathrm{FFT}}=960\) at 48 kHz with 50% overlap ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)).

\(f_s=16\,\mathrm{kHz}\), \(L=512\), \(R=256\): \(T_L=512/16000=32\,\mathrm{ms}\), \(T_R=16\,\mathrm{ms}\), hops/s \(=62.5\). (Dividing samples by \(f_s\) is the whole calculation; 512 samples is not 16 ms at 16 kHz.)

A 10 ms hop at 16 kHz is \(R=160\), not 256.

### Broken COLA symptom

Amplitude tremolo at \(f_s/R\) Hz (e.g. 100 Hz for a 10 ms hop). Listeners say “robotic” or “phasey.” A neural gain bug does not lock to exactly \(f_s/R\); a COLA bug does.

### Warm-up

The first \(L-R\) samples may be incomplete — discard or fade them before you score SI-SDR.

## Common pitfalls

1. Analysis Hann + synthesis rectangular without checking COLA.
2. Changing hop but reusing windows from another hop.
3. Emitting full \(L\) samples every hop (massive overlap redundancy / desync).
4. Clearing OLA memory each callback.
5. Offline STFT (center-padded) vs streaming STFT mismatch in eval.

## Mini-lab

**Goal.** Overlap-add a periodic Hann at 50% hop and check that the sum is exactly flat in the interior.

```python
import numpy as np

L, R = 256, 128
n = np.arange(L)
w = 0.5 - 0.5 * np.cos(2 * np.pi * n / L)  # periodic Hann, not np.hann default
N = L + 8 * R
acc = np.zeros(N)
for m in range(0, N - L + 1, R):
    acc[m:m + L] += w
mid = acc[L:N - L]
print("COLA constant", float(mid[0]))
print("peak deviation", float(np.max(np.abs(mid - mid[0]))))
```

**Expected.** The printed constant is `1.0`. The peak deviation is on the order of \(10^{-15}\).

**Failure modes.** `np.hann(L)` (symmetric) makes the deviation jump to about \(10^{-2}\) or worse: the endpoints are both zero, so the pairwise sum derived above is not 1. Summing `w**2` instead of `w` prints a constant that wanders between 0.5 and 1 — that is the double-window ripple, and the assertion must fail. A hop of `L/4` with this same `w` is also not flat; 50% is the hop the identity used.

## Mini exercises

1. Overlap ratio for \(L=1024\), \(R=256\)?
2. Hop ms at 16 kHz with \(R=160\)?
3. Why does smaller hop increase CPU?
4. Sketch OLA buffer after 3 hops of length \(L=8\), \(R=4\) (toy).
5. Name one test signal to verify COLA (hint: impulse or linear chirp).

### Answer hints

1. \(\rho=1-256/1024=0.75\).
2. \(160/16000=10\,\mathrm{ms}\).
3. hops/s \(=f_s/R\) rises, and you run an FFT on every hop.
4. After three hops the accumulator holds a full interior region of length \(R\) where two windows overlap, plus a tail of length \(L-R\).
5. An impulse (or a constant) makes a non-flat COLA sum visible as a periodic amplitude envelope; a chirp also exposes time smearing.

## Further reading

- Oppenheim & Schafer — STFT / filterbank / OLA sections.
- Julius O. Smith, *Spectral Audio Signal Processing* — COLA and the Hann identity.
- DeepFilterNet framing: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
