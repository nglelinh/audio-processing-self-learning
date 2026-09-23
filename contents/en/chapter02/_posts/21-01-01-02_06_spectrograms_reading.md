---
layout: post
title: "02-06 Spectrograms: reading speech and noise"
chapter: "02"
order: 6
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Spectrograms are the shared language of speech engineers. This lesson trains you to read speech structure, noise types, and NS artifacts visually — and to avoid lying dB scales. A spectrogram is not a picture of “the audio.” It is \(|X(\ell,k)|\) from a specific STFT, in decibels, with a floor. Change the window or the color scale and you change the story.

## Learning objectives

1. Interpret spectrogram axes (time, frequency, dB color).
2. Recognize voiced harmonics, formants, fricatives, and silence.
3. Identify stationary noise floors, bursts, babble, and music.
4. Spot common NS artifacts (musical noise, over-suppression, warble).
5. Use spectrograms responsibly alongside listening and metrics.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Anatomy of a spectrogram plot |
| 10–28 | Speech patterns gallery (describe without audio) |
| 28–42 | Noise gallery + mixture reading |
| 42–52 | Before/after NS artifact reading |
| 52–60 | Exercises |

![A speech spectrogram: stacked horizontal harmonic lines, then a vertical broadband noise burst]({{ site.imgurl }}/generated/spectrogram-reading.png)

*Figure. Voiced harmonics are a vertical stack of ridges; a noise burst is a vertical bar that fills every band at once.*

## Core explanations

### Axes and scaling

- **X:** time (s) or frame index.
- **Y:** Hz (linear) or Mel/ERB (perceptual).
- **Color:** usually \(20\log_{10}|X(\ell,k)|\) with a floor clamp.

Always record: \(f_s\), window, hop, FFT size, dB range (e.g. −80..0 dB). Without these, screenshots are not science.

The color computation is worth writing once:

$$
S(\ell,k)=20\log_{10}\bigl(\max(|X(\ell,k)|,\,\varepsilon)\bigr).
$$

\(\varepsilon\) is the floor. Without it, a silent bin (exact zero after a hard mask) becomes \(-\infty\) and the colormap stretches around a single hole, so the rest of the utterance looks like a flat beige bar. With a floor at, say, −80 dB relative to a full-scale sine, silence is a dark color and a vowel’s harmonics stay visible. Two screenshots are comparable only when \(\varepsilon\), the window, and the hop match. A Mel axis will not line up with linear-bin bugs: bin \(k\) maps to \(k f_s/N\) hertz, and a Mel filterbank has already summed those bins.

### A reading procedure

Use the figure as the worked case, then the same order on every bug-ticket image.

1. **Stamp the STFT.** Read \(f_s\), window, hop, \(N\), and the dB range off the caption before you interpret color. The figure’s ridges sit near 1.2, 2.4, 3.6, 4.8, 6.0, and 7.2 kHz: a 1.2 kHz fundamental and its harmonics, drawn on a linear hertz axis.
2. **Find silence or the noise floor.** The dark regions before 0.2 s and after the burst are the floor. If that floor is already bright, either the mic is hissy or the color scale is zoomed into the bottom 20 dB. Do not call the model “under-suppressing” until you know which.
3. **Look for a harmonic stack.** Horizontal ridges, equally spaced, mean voiced speech (or music). Spacing is \(f_0\). In the figure the gap is about 1.2 kHz, which is a high pitched vowel or a sung note, not a typical 100–200 Hz speaking voice — the geometry is the same, the spacing is the pitch.
4. **Look for vertical events.** A plosive or a noise burst lights many bins in one or two frames. The orange bar from about 0.85 s to 1.0 s is that: energy at every frequency, not a new harmonic. Keyboard clicks and coughs look similar and narrower.
5. **Only then compare before and after NS**, on the same scale. Missing upper ridges mean over-suppression of harmonics. Speckles in the dark region mean musical noise. Periodic light/dark time stripes locked to the hop mean COLA or gain pumping, not “more noise.”

Phase errors never appear in \(S(\ell,k)\). A watery residual with a clean magnitude spectrogram is a phase-reuse problem (lesson 02-04), and the picture will not confess.

### Speech landmarks

| Pattern | Look |
|---------|------|
| Voiced vowel | Harmonic striations; dark formant bands |
| Pitch change | Striations tilt / spacing change |
| Plosive | Vertical broadband burst + closure gap |
| Fricative | High-frequency noisy cloud |
| Silence | Near floor (mic noise remaining) |

### Noise landmarks

| Noise | Look |
|-------|------|
| HVAC | Low-frequency persistent ridge |
| Fan hiss | Elevated broadband floor |
| Keyboard | Thin vertical spikes |
| Babble | Speech-like but unruly competing structure |
| Music | Stable harmonic stacks unlike speech formant motion |

### Artifact landmarks after NS

| Artifact | Look / sound |
|----------|--------------|
| Musical noise | Speckled isolated bins in time |
| Over-suppression | Missing fricative clouds; muffled |
| Hop warble | Periodic amplitude stripes at hop rate |
| Residual reverb | Vertical smearing lasting after speech |

### Good practice

Spectrogram **supports** listening and SI-SDR/DNSMOS (Ch. 08); it does not replace them. A pretty spectrogram can still sound bad (phase issues invisible on mag plots).

## Worked examples

### Parameter stamp

“48 kHz, Hann 20 ms, hop 10 ms, N=1024, dB −70..0” — reproducible. Note \(N=1024\) at 48 kHz is about 21.3 ms if the window equals the FFT, which is *not* the DeepFilterNet 960-point grid. Say so in the ticket or you will “fix” the wrong bins.

### Which bins hold the harmonics

Bin center frequency is \(k f_s/N\). A 200 Hz harmonic at \(f_s=8\,\mathrm{kHz}\), \(N=256\), falls at

$$
k=\frac{200}{8000/256}=6.4,
$$

so the energy straddles bins 6 and 7. The second and third harmonics straddle 12–13 and land near 19. The mini-lab prints those bins. If your bug report says “the tone is in bin 200,” you mixed hertz with bin index.

### Misread

Bright low-frequency bar might be DC bias, not “noise the model failed.” High-pass before plotting if diagnosing NS.

### Babble vs target

Both show harmonics; target often louder/closer (higher SNR tracks). Single-channel NS struggles — spectrogram sets expectations.

## Common pitfalls

1. Comparing plots with different dB color ranges.
2. Using Mel plots to debug linear-STFT bin bugs.
3. Declaring victory from a quieter floor alone (speech may be damaged).
4. Ignoring that phase artifacts are mag-invisible.
5. Ultra-long windows that make everything look “stationary.”

## Mini-lab

**Goal.** Build a tiny spectrogram from `rfft` frames of a three-harmonic sine and print which bins light up.

```python
import numpy as np

fs, L, R = 8000, 256, 128
t = np.arange(int(0.4 * fs)) / fs
f0 = 200.0
x = (np.sin(2 * np.pi * f0 * t)
     + 0.5 * np.sin(2 * np.pi * 2 * f0 * t)
     + 0.25 * np.sin(2 * np.pi * 3 * f0 * t))
w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(L) / L)
frame = x[L:L + L] * w
mag = np.abs(np.fft.rfft(frame))
# one column of the spectrogram; bin k <-> k * fs / L Hz
top = np.argsort(mag)[-6:][::-1]
print("top bins", top.tolist())
for h in (1, 2, 3):
    print(f"harmonic {h} expected k", h * f0 * L / fs)
```

**Expected.** Expected centers are **6.4, 12.8, 19.2**. The strongest bins are the neighbors of those centers (typically 6 and 7 for 200 Hz, 12 and 13 for 400 Hz, and 19 for 600 Hz). That pair-of-bins pattern is leakage of an off-grid harmonic through the Hann main lobe, not noise.

**Failure modes.** Printing `np.argmax(mag)` only returns bin 6 and hides the other harmonics. Using `fft` instead of `rfft` duplicates the spectrum and shifts the index story. Forgetting the window makes sidelobes (lesson 02-03) promote unrelated bins into the top six. Interpreting bin 6 as 6 Hz instead of \(6\cdot8000/256=187.5\,\mathrm{Hz}\) is the usual ticket bug.

## Mini exercises

1. Sketch a spectrogram cartoon of “hello” in noise.
2. How would 10 ms hop COLA failure appear?
3. Why clamp log floors?
4. Name two cues distinguishing music interference from voiced speech.
5. What metadata must accompany a spectrogram in a bug ticket?

### Answer hints

1. A low-frequency harmonic stack for the vowel, a high-frequency cloud for the fricative, a vertical burst for the /h/ or the stop, on top of a steady floor.
2. Vertical light/dark stripes every 10 ms, locked to the hop, including through steady vowels.
3. Otherwise exact zeros become \(-\infty\) and the color scale collapses.
4. Music keeps rigid harmonic spacing and long stable partials; speech moves its formants and changes \(f_0\) with prosody.
5. \(f_s\), window, hop, FFT size, and dB range.

## Further reading

- Oppenheim & Schafer, and Julius O. Smith’s spectral audio notes — what a short-time magnitude actually measures.
- Speech processing textbooks’ spectrogram chapters (standard DSP/speech notes).
- DNS Challenge visualization examples (dataset pages) and DeepFilterNet paper figures; read the axes before comparing them to a 48 kHz linear STFT.
