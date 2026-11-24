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

A spectrogram is to an audio engineer what an X-ray is to a radiologist—and just like an X-ray, changing the contrast knob can make a healthy lung look broken or hide a fracture completely. A spectrogram is **not** a raw picture of “the audio”; it is $$20\log_{10}(\max(\vert X(\ell, k)\vert, \varepsilon))$$ computed from one specific STFT window, hop, and dB floor!

This lesson trains your eye to read speech anatomy (harmonics, formants, plosives, fricatives), noise signatures (HVAC, clicks, babble), and enhancement artifacts (musical noise speckles, hop-rate COLA stripes, over-suppression)—while remembering the one thing every magnitude spectrogram hides: **phase**.

![A speech spectrogram: stacked horizontal harmonic lines, then a vertical broadband noise burst]({{ site.imgurl }}/generated/spectrogram-reading.png)

*Figure. Voiced harmonics are a vertical stack of ridges; a noise burst is a vertical bar that fills every band at once.*

**Lesson roadmap:** Background Knowledge Map (log-magnitude color scales, speech vs. noise time–frequency geometry, what spectrograms hide) → 5-step diagnostic reading procedure & landmark tables → Worked examples: mapping 200/400/600 Hz harmonics to fractional bins $$6.4, 12.8, 19.2$$ and stamping reproducible plot metadata → Deep-Dive Explanation (Read Slowly): 3-step visual triage of before/after NS spectrograms → Pitfalls, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: Visual Diagnostics in Time–Frequency Space

### 1. Decibel Compression and the Floor Clamp $$\varepsilon$$
Human hearing spans over 100 dB of dynamic range; plotting raw linear magnitude $$\vert X(\ell, k)\vert$$ makes quiet fricatives and noise floors invisible next to loud vowels. Taking $$S(\ell, k) = 20\log_{10}(\max(\vert X(\ell, k)\vert, \varepsilon))$$ reveals subtle structure, provided you fix a consistent floor (e.g., $$-80\,\mathrm{dB}$$) across before/after comparisons.

### 2. Geometry of Speech vs. Noise
- **Horizontal stacks** = periodic pitched energy (voiced vowels, music), spaced by fundamental frequency $$f_0$$.
- **Broad dark blobs across harmonics** = vocal-tract **formants** that carry vowel identity.
- **Vertical broadband bars** = sharp time transients (plosives /p/, /t/, /k/, keyboard clicks, door slams).
- **High-frequency diffuse clouds** = unvoiced fricatives (/s/, /f/, /sh/) or fan hiss.

### 3. The Blind Spot: Phase Is Invisible
A magnitude spectrogram discards $$\arg X(\ell, k)$$ completely. Two clips can have *identical* clean-looking spectrograms while one sounds crisp and the other sounds hollow and metallic due to noisy phase reuse or broken Hermitian symmetry—which is why spectrograms always **pair with**, never replace, listening.

---

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

## Core explanations

### Axes and scaling

- **X:** time (s) or frame index.
- **Y:** Hz (linear) or Mel/ERB (perceptual).
- **Color:** usually $$20\log_{10}\vert X(\ell,k)\vert$$ with a floor clamp.

Always record: $$f_s$$, window, hop, FFT size, dB range (e.g. −80..0 dB). Without these, screenshots are not science.

The color computation is worth writing once:

$$
S(\ell,k)=20\log_{10}\bigl(\max(\vert X(\ell,k)\vert,\,\varepsilon)\bigr).
$$

$$\varepsilon$$ is the floor. Without it, a silent bin (exact zero after a hard mask) becomes $$-\infty$$ and the colormap stretches around a single hole, so the rest of the utterance looks like a flat beige bar. With a floor at, say, −80 dB relative to a full-scale sine, silence is a dark color and a vowel’s harmonics stay visible. Two screenshots are comparable only when $$\varepsilon$$, the window, and the hop match. A Mel axis will not line up with linear-bin bugs: bin $$k$$ maps to $$k f_s/N$$ hertz, and a Mel filterbank has already summed those bins.

### A reading procedure

Use the figure as the worked case, then the same order on every bug-ticket image.

1. **Stamp the STFT.** Read $$f_s$$, window, hop, $$N$$, and the dB range off the caption before you interpret color. The figure’s ridges sit near 1.2, 2.4, 3.6, 4.8, 6.0, and 7.2 kHz: a 1.2 kHz fundamental and its harmonics, drawn on a linear hertz axis.
2. **Find silence or the noise floor.** The dark regions before 0.2 s and after the burst are the floor. If that floor is already bright, either the mic is hissy or the color scale is zoomed into the bottom 20 dB. Do not call the model “under-suppressing” until you know which.
3. **Look for a harmonic stack.** Horizontal ridges, equally spaced, mean voiced speech (or music). Spacing is $$f_0$$. In the figure the gap is about 1.2 kHz, which is a high pitched vowel or a sung note, not a typical 100–200 Hz speaking voice — the geometry is the same, the spacing is the pitch.
4. **Look for vertical events.** A plosive or a noise burst lights many bins in one or two frames. The orange bar from about 0.85 s to 1.0 s is that: energy at every frequency, not a new harmonic. Keyboard clicks and coughs look similar and narrower.
5. **Only then compare before and after NS**, on the same scale. Missing upper ridges mean over-suppression of harmonics. Speckles in the dark region mean musical noise. Periodic light/dark time stripes locked to the hop mean COLA or gain pumping, not “more noise.”

Phase errors never appear in $$S(\ell,k)$$. A watery residual with a clean magnitude spectrogram is a phase-reuse problem (lesson 02-04), and the picture will not confess.

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

“48 kHz, Hann 20 ms, hop 10 ms, N=1024, dB −70..0” — reproducible. Note $$N=1024$$ at 48 kHz is about 21.3 ms if the window equals the FFT, which is *not* the DeepFilterNet 960-point grid. Say so in the ticket or you will “fix” the wrong bins.

### Which bins hold the harmonics

Bin center frequency is $$k f_s/N$$. A 200 Hz harmonic at $$f_s=8\,\mathrm{kHz}$$, $$N=256$$, falls at

$$
k=\frac{200}{8000/256}=6.4,
$$

so the energy straddles bins 6 and 7. The second and third harmonics straddle 12–13 and land near 19. The mini-lab prints those bins. If your bug report says “the tone is in bin 200,” you mixed hertz with bin index.

### Misread

Bright low-frequency bar might be DC bias, not “noise the model failed.” High-pass before plotting if diagnosing NS.

### Babble vs target

Both show harmonics; target often louder/closer (higher SNR tracks). Single-channel NS struggles — spectrogram sets expectations.

---

### Deep-Dive Explanation: How to Read a Before/After NS Spectrogram Without Getting Fooled (Read Slowly)

#### Step 1: Lock identical STFT and dB color limits on both panels
Always plot `noisy` and `enhanced` with the exact same `vmin=-80, vmax=0` (dB), same window, and same linear Hz axis. Auto-scaling each plot independently makes a quiet clean clip look just as bright as a noisy one!

#### Step 2: Check speech preservation BEFORE celebrating a dark noise floor
Inspect high-frequency fricative clouds (4–10 kHz) and upper vocal harmonics during active speech. If the background turned pitch-black *only* because the suppressor shaved off everything above 3 kHz, listeners will hear a muffled, underwater voice.

#### Step 3: Hunt for geometric artifact fingerprints
- **Salt-and-pepper speckles** in quiet pauses $$\implies$$ **musical noise** (too little time/frequency gain smoothing).
- **Regular vertical zebra stripes** spaced every hop $$R$$ $$\implies$$ **broken COLA** or callback underrun, not model error.
- **Clean-looking plot that still sounds hollow** $$\implies$$ **phase corruption** (invisible on magnitude plots; check complex filtering / Hermitian symmetry).

Summary of spectrogram diagnostics:

$$
S(\ell, k) = 20\log_{10}\max(\vert X(\ell,k)\vert, \varepsilon)
\;\xrightarrow{\text{Same scale}}\;
\text{Harmonics + Fricatives + Artifacts}
\;\xrightarrow{+ \text{Ears}}\;
\text{Root cause}.
$$

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

**Failure modes.** Printing `np.argmax(mag)` only returns bin 6 and hides the other harmonics. Using `fft` instead of `rfft` duplicates the spectrum and shifts the index story. Forgetting the window makes sidelobes (lesson 02-03) promote unrelated bins into the top six. Interpreting bin 6 as 6 Hz instead of $$6\cdot8000/256=187.5\,\mathrm{Hz}$$ is the usual ticket bug.

## Mini exercises

1. Sketch a spectrogram cartoon of “hello” in noise.
2. How would 10 ms hop COLA failure appear?
3. Why clamp log floors?
4. Name two cues distinguishing music interference from voiced speech.
5. What metadata must accompany a spectrogram in a bug ticket?

### Answer hints

1. A low-frequency harmonic stack for the vowel, a high-frequency cloud for the fricative, a vertical burst for the /h/ or the stop, on top of a steady floor.
2. Vertical light/dark stripes every 10 ms, locked to the hop, including through steady vowels.
3. Otherwise exact zeros become $$-\infty$$ and the color scale collapses.
4. Music keeps rigid harmonic spacing and long stable partials; speech moves its formants and changes $$f_0$$ with prosody.
5. $$f_s$$, window, hop, FFT size, and dB range.

## Further reading

- Oppenheim & Schafer, and Julius O. Smith’s spectral audio notes — what a short-time magnitude actually measures.
- Speech processing textbooks’ spectrogram chapters (standard DSP/speech notes).
- DNS Challenge visualization examples (dataset pages) and DeepFilterNet paper figures; read the axes before comparing them to a 48 kHz linear STFT.

## Video tham khảo

- [The Spectrogram and the Gabor Transform](https://www.youtube.com/watch?v=EfWnEldTyPA) — Steve Brunton, English. **xem trước.** Watch how a sliding window becomes a time-frequency image. Read axes before colors; that is the spectrogram this lesson asks you to trust.
- [Speech Acoustics 5 - vowel formants](https://www.youtube.com/watch?v=glnUFa2fLyE) — Listen Lab, English. Watch the dark bands, not every harmonic. Formants are the speech structure a noise suppressor must not erase.
- [Coding Adventure: Analyzing Audio](https://www.youtube.com/watch?v=08mmKNLQVHU) — Sebastian Lague, English. The short-time section shows a voice sliced into frames and drawn as a spectrogram, including how a single full-file FFT lies about timing.
