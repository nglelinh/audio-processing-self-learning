---
layout: post
title: "02-03 Windowing and spectral leakage"
chapter: "02"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Even if you “never applied a window” to your audio frame, you already applied one—the harshest window in signal processing: a **rectangular chop** that slams your waveform to zero at both ends of the buffer. That abrupt cliff smears every off-bin vocal harmonic across dozens of neighboring FFT bins with sidelobes only **13 dB** below the main peak—loud enough to fool a noise estimator and trigger metallic “musical noise” chirps!

Tapering the frame smoothly to zero with a **Hann window** crushes that first sidelobe down to **−31 dB** (an 18 dB cleaner floor) at the cost of a slightly wider main lobe. This lesson unpacks the exact main-lobe vs. sidelobe tradeoff, why window gain shifts Parseval checks by 6 dB, and why you should always test windows on a *half-bin* tone.

![Rectangular window versus Hann: the rectangular transform keeps a slow sinc tail, the Hann transform drops its sidelobes and widens the main lobe]({{ site.imgurl }}/generated/window-leakage.png)

*Figure. Peak-normalized magnitude of a windowed tone: the rectangular window leaks a slow sidelobe tail, while the Hann window trades a wider main lobe for a much lower floor.*

**Lesson roadmap:** Key ideas (time multiplication = spectral convolution, main-lobe vs. sidelobe tradeoff, window gain & COLA) → Window catalog (Rectangular, Hann, Hamming, Blackman) → Resolution tradeoffs & musical noise → Worked examples: 48 kHz Hann main-lobe width (200 Hz) and testing a half-bin tone (bin 32.5) → Explanation: 3 steps from edge discontinuity to −31 dB sidelobes → Pitfalls, Mini-lab, Exercises & Videos.

---

## Key ideas: Spectral Leakage and Window Design

### 1. Time Multiplication = Frequency Convolution
Extracting a finite frame multiplies the infinite signal $$x[n]$$ by a window $$w[n]$$. In frequency, that **convolves** the true spectrum $$X(e^{j\omega})$$ with the window’s Fourier transform $$W(e^{j\omega})$$. Every pure sinusoid stops being a razor-thin spike and becomes a copy of $$W(e^{j\omega})$$ centered at its frequency!

### 2. The Universal Tradeoff: Main-Lobe Width vs. Sidelobe Height
A window’s spectrum $$W(e^{j\omega})$$ has two competing features:
- **Main-lobe width** (controls how close two tones can sit before merging into one blob—narrowest for Rectangular at ~2 bins, wider for Hann at ~4 bins).
- **Sidelobe height** (controls how much energy leaks into distant bins—poor for Rectangular at $$-13\,\mathrm{dB}$$, much cleaner for Hann at $$-31\,\mathrm{dB}$$).

### 3. Window Gain and Why Independent-Bin Masks Cause Musical Noise
Because a Hann window has mean $$1/2$$, multiplying a signal by it drops broadband magnitude by half ($$\approx -6\,\mathrm{dB}$$)—which you must account for in Parseval/PSD checks. Furthermore, because real harmonics spill across adjacent bins inside $$W(e^{j\omega})$$, hard per-bin masking chops sidelobes unevenly and creates isolated flickering peaks (**musical noise**).

---

## Learning objectives

1. Explain spectral leakage from rectangular truncation.
2. Compare common windows (Hann, Hamming, Blackman) qualitatively.
3. Connect main-lobe width to frequency resolution and time localization.
4. State how windows interact with COLA and NS masking.
5. Choose windows consistently with a pretrained STFT front-end.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Rectangular window leakage demo (thought/plot) |
| 12–28 | Window catalog; sidelobe vs main lobe |
| 28–42 | COLA + window choice; doubling windows |
| 42–52 | Musical noise link to bin independence myth |
| 52–60 | Exercises |

## Core explanations

### Leakage mechanism

Multiplying by $$w[n]$$ convolves the DTFT with $$W(e^{j\omega})$$. Rectangular $$w$$ has high sidelobes → distant bins contaminated. Tapered windows lower sidelobes, widen main lobe → nearby bins blurred together.

A finite frame is already a multiply by a rectangle, even when you “did not apply a window.” The DTFT of that rectangle is a Dirichlet kernel. Its first sidelobe peaks about **13 dB below** the main lobe, and the tail falls slowly. A tone that misses the bin center — every real speech harmonic eventually does — dumps energy tens of bins away at a level a noise tracker can mistake for noise.

The Hann window is the periodic raised cosine from lesson 02-02,

$$
w[n]=\frac12-\frac12\cos\frac{2\pi n}{L}.
$$

Its transform cancels that slow tail: the first sidelobe falls to about **−31 dB**, roughly 18 dB quieter, and the far sidelobes keep falling. The price is main-lobe width, about four bins null-to-null instead of two. Lengthening $$L$$ and switching to Hann are different knobs.

The figure is that comparison. Read the axis as dB relative to the peak.

### Qualitative comparison

| Window | Sidelobes | Main lobe | Notes |
|--------|-----------|-----------|-------|
| Rectangular | poor (first sidelobe ≈ −13 dB) | narrowest (~2 bins) | analysis curiosity; implicit if you skip windowing |
| Hann | good (first sidelobe ≈ −31 dB) | wider (~4 bins) | STFT favorite; COLA @ 50% with the periodic form |
| Hamming | similar | similar | sidelobe floor differs; not the same COLA identity |
| Blackman | lower sidelobes | wider | more smoothing; do not swap in for a Hann model |

Exact coefficients are standard; copy from a DSP reference when implementing — do not invent. Hamming’s endpoints are not zero, so it is a poor drop-in replacement for a Hann COLA pair even though the plots “look alike.”

### Resolution tradeoff

Effective frequency resolution $$\sim \alpha f_s/L$$ with $$\alpha>1$$ depending on window. Time localization $$\sim L/f_s$$. Speech NS wants enough resolution to separate formants/noise floors, enough time locality for consonants — hence mid-length windows (tens of ms), not 1 ms and not 1 s.

At 48 kHz with $$L=960$$, a Hann main lobe of about four bins is $$4\cdot48000/960=200\,\mathrm{Hz}$$ wide. It will not split harmonics of a low voice, and it smears a 5 ms plosive across the 20 ms window. Finer bins mean a longer $$L$$ and more latency. Less distant leakage means a different window, not zero-padding: padding interpolates $$W(e^{j\omega})$$, it does not narrow it.

### Windows and masks

Neural/classical gains that jump wildly across adjacent bins fight the window’s inherent smoothing — or create musical noise when bins are treated as independent. Smooth masks in frequency (and time) match physics better. A rectangular analysis makes the “independent bin” assumption especially false: bin $$k+8$$ still contains the tone from bin $$k$$ at a level you can hear. Suppressing “noise bins” with a hard gate then chops the sidelobes of the vowel and leaves the main lobe, which is one recipe for musical noise even before the noise estimate is wrong.

### Analysis vs synthesis

Some pipelines use $$w$$ on analysis only and a different synthesis window for COLA. Others use $$\sqrt{\text{Hann}}$$ on both (power complementary designs). **Match training.** Randomly switching to Blackman “for quality” breaks reconstruction. Lesson 02-02 showed why the square of a Hann is not COLA: the product $$w\cdot w$$ ripples between $$1/2$$ and $$1$$. The square root splits that window so each side is tapered and the product still sums flat.

Window gain also moves Parseval checks. A Hann has mean $$1/2$$, so an unnormalized analysis cuts broadband power by about 6 dB before any suppressor runs. SI-SDR against a time-domain reference will look like a systematic loss until you divide by the COLA constant or compensate the synthesis gain.

## Worked examples

### On-bin vs off-bin

16 kHz, $$L=512$$, tone exactly bin 32 vs bin 32.5. Rectangular: off-bin spreads widely. Hann: sidelobes drop, main lobe wider — both bins 32 and 33 light up. An on-bin tone under a periodic window can look almost ideal (sidelobes at numerical floor) and will hide a bad window choice. Always test a half-bin offset. The mini-lab does that and prints the empirical sidelobe, which is not identical to the −13 / −31 dB textbook peaks because the peak sits between bins and the measurement skips a guard around it; the gap between rectangle and Hann is the same lesson as the figure.

### Musical noise

Spectral subtraction with independent bin floors → isolated bin spikes surviving as birdies. Over-smoothing helps but blurs speech — classic tension before neural SE.

---

### Explanation: Why Tapering to Zero Crushes Sidelobes by 18 dB

#### Step 1: See why the rectangular window leaks slowly ($$1/f$$ decay)
Under periodic extension, an off-bin sine wave jumps abruptly between sample $$L-1$$ and sample $$0$$—a step discontinuity! The Fourier transform of a step discontinuity decays slowly as $$1/f$$, leaving high sidelobes ($$-13\,\mathrm{dB}$$ at the first peak) far away from the true tone.

#### Step 2: Decompose the Hann window into three shifted sincs
Write $$w[n] = \frac{1}{2} - \frac{1}{4}e^{j2\pi n/L} - \frac{1}{4}e^{-j2\pi n/L}$$. In frequency, its transform $$W(\omega)$$ is a central rectangular sinc **minus** two half-amplitude sincs shifted by $$\pm 1$$ bin! In the far tails, those opposite-sign sinc lobes cancel each other out, speeding the decay from $$1/f$$ to $$1/f^3$$ and dropping the first sidelobe from $$-13\,\mathrm{dB}$$ to $$-31\,\mathrm{dB}$$!

#### Step 3: Always test window leakage at a half-bin frequency ($$k + 0.5$$)
At an integer bin $$k$$, the zeros of the rectangular Dirichlet kernel land *right on top of* all other FFT bins, creating an illusion of zero leakage. Testing at $$k + 0.5$$ places every other bin right on the sidelobe peaks—exposing the real gap between Rectangular and Hann!

Summary of the windowing tradeoff:

$$
x[n]\cdot w[n]
\;\xleftrightarrow{\text{DTFT}}\;
X * W
\;\Longrightarrow\;
\text{Rect } (-13\,\mathrm{dB},\ 2\text{ bins})
\;\text{vs.}\;
\text{Hann } (-31\,\mathrm{dB},\ 4\text{ bins}).
$$

## Common pitfalls

1. Applying window twice unintentionally (pre-windowed API + manual window).
2. Using rectangular for NS because “FFT needs it.”
3. Ignoring window gain when checking Parseval / SI-SDR.
4. Different windows in train vs serve.
5. Expecting window alone to fix aliasing (it will not).

## Mini-lab

**Goal.** FFT one off-bin sine under a rectangular window and under a periodic Hann, and print the sidelobe level in dB relative to the peak.

```python
import numpy as np

fs, N = 16000, 512
n = np.arange(N)
f = 32.5 * fs / N  # halfway between bins 32 and 33
x = np.sin(2 * np.pi * f * n / fs)
hann = 0.5 - 0.5 * np.cos(2 * np.pi * n / N)

def sidelobe_db(mag, guard=3):
    mag = mag / mag.max()
    k = int(np.argmax(mag))
    side = np.concatenate([mag[: max(0, k - guard)], mag[k + guard + 1 :]])
    return 20 * np.log10(side.max())

rect = np.abs(np.fft.rfft(x))
han = np.abs(np.fft.rfft(x * hann))
print("rect sidelobe dB", round(float(sidelobe_db(rect)), 1))
print("hann sidelobe dB", round(float(sidelobe_db(han)), 1))
```

**Expected.** Rectangular sidelobe near **−17 dB**, Hann near **−40 dB** (guard of 3 bins around an off-bin peak). The Hann number is lower, and the main lobe is the wider of the two if you plot them.

**Failure modes.** An integer bin (`32 * fs / N`) drives both sidelobes to the numerical floor (below −200 dB) and teaches nothing. `np.hann` versus the periodic formula changes the Hann number slightly but should not close the gap. Forgetting to normalize by `mag.max()` prints absolute FFT units, not dB relative to the peak. A guard of 0 reports the main-lobe shoulder as a “sidelobe” and both windows look similarly bad.

## Mini exercises

1. Why do tapered windows reduce sidelobes?
2. If $$L$$ doubles, what happens to main-lobe width roughly?
3. Name a COLA-friendly hop for Hann (common choice).
4. How can aggressive per-bin masks create musical noise?
5. Give one reason $$\sqrt{\text{Hann}}$$ appears in STFT codebases.

### Answer hints

1. The window’s transform $$W$$ has smaller sidelobes, and multiplication by $$w$$ convolves the tone with $$W$$.
2. Width in hertz scales as $$f_s/L$$, so it halves; width in bins stays about 4 for a Hann.
3. $$R=L/2$$ for the periodic Hann (lesson 02-02).
4. Hard zeros between bins chop the sidelobes of a real harmonic and leave isolated peaks that chirp after ISTFT.
5. So analysis and synthesis can each be tapered while their product still satisfies COLA.

## Further reading

- Oppenheim & Schafer — windows and spectral analysis.
- Julius O. Smith, *Spectral Audio Signal Processing* — sidelobe level and main-lobe width.
- DeepFilterNet STFT configuration: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588).

## Video tham khảo

- [Lecture 13: Spectral Leakage, Windowing, with Examples of Hanning and Hamming Windows](https://www.youtube.com/watch?v=tCWU9C-LdJQ) — Bahga Lab IIT Delhi, English. **xem trước.** Watch the rectangular sidelobes against Hann and Hamming. That main-lobe versus leakage trade is the whole lesson.
- [The more general uncertainty principle, regarding Fourier transforms](https://www.youtube.com/watch?v=MBnnXbOM5S4) — 3Blue1Brown, English. A shorter window is a shorter observation. The uncertainty section says why the main lobe must widen.
- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, English. The window-multiply step shows the same taper on a speech frame, which is where leakage becomes musical noise later.
