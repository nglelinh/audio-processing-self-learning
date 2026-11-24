---
layout: post
title: "03-01 Spectral subtraction"
chapter: "03"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter03
lesson_type: required
draft: false
---

If you had to invent a noise suppressor from scratch in one afternoon, your first instinct would probably be Steven Boll’s 1979 classic: listen during a brief pause to measure the noise spectrum $$\widehat{\vert N\vert}$$, subtract it from every noisy STFT frame $$\vert Y\vert$$, clip any negative remainders to zero, and invert back to audio.

It works astonishingly well on steady fan hum—and then, the moment you listen closely to the quiet pauses, you hear eerie, twinkling electronic “birdies” chirping at random pitches. That iconic artifact (**musical noise**) is the single best teacher in classical speech enhancement. This lesson builds magnitude spectral subtraction with over-subtraction $$\alpha$$ and flooring $$\beta$$, walks through concrete bin calculations by hand, and explains when a cheap classical subtractor still sits in front of a neural model.

![Power-domain spectral subtraction per bin, next to a Wiener gain curve that this lesson does not yet apply]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Figure. Spectral subtraction (left) removes a noise floor and then floors the remainder; the smooth curve on the right is the Wiener gain you get once subtraction becomes an SNR.*

**Lesson roadmap:** Background Knowledge Map (magnitude-only estimation & noisy phase, noise-floor tracking, why musical noise happens) → Over-subtraction $$\alpha$$ & spectral floor $$\beta$$ + pseudocode → Worked example: 3-bin hand calculation showing why flooring prevents spectral holes → Deep-Dive Explanation (Read Slowly): 3 steps explaining how random noise peaks turn into “musical birdies” → Classical front-end use cases, Pitfalls, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: Classical Spectral Subtraction and Noise-Floor Tracking

### 1. Magnitude-Only Subtraction & Noisy Phase Reuse
Under additive noise $$Y(k, \ell) = S(k, \ell) + N(k, \ell)$$, spectral subtraction estimates only the clean **magnitude** $$\vert \hat{S}\vert$$ and keeps the **noisy phase** $$\angle Y$$. Because human hearing tolerates moderate phase error at high SNR ($$\ge 5\,\mathrm{dB}$$), this shortcut is fast and lightweight—though it breaks down in heavy noise.

### 2. Noise-Floor Estimation Under Stationarity
Every classical subtractor lives or dies by its noise estimate $$\widehat{\vert N\vert}(k, \ell)$$, typically updated recursively during non-speech frames via Voice Activity Detection (VAD) or minimum-statistics tracking. When background noise is stationary (HVAC), the estimate stays accurate; when noise is impulsive or speech-like (keyboard, babble), the tracker lags.

### 3. Over-Subtraction ($$\alpha$$) and Spectral Flooring ($$\beta$$)
Because instantaneous noise fluctuates randomly around its mean $$\widehat{\vert N\vert}$$, subtracting $$1.0\times \widehat{\vert N\vert}$$ leaves half of the noise bins slightly positive and clips the other half to zero. Engineers introduce **over-subtraction $$\alpha \ge 1$$** to push residual peaks down and a **spectral floor $$\beta \in (0, 1)$$** to fill hard zero holes with a gentle broadband cushion.

---

## Learning objectives

By the end of this lesson you will be able to state the additive mixture model in the STFT domain, write magnitude spectral subtraction with over-subtraction and flooring in pseudocode, explain why residual peaks sound like musical tones, and decide when a classical subtractor is a useful pre-stage versus when you should jump straight to a Wiener or neural masker.

## 60-minute teaching plan

- **0–10 min** — Additive model $$Y = S + N$$, magnitude vs power spectra, and why phase is usually kept from the noisy frame.
- **10–25 min** — Noise estimation (VAD / min-statistics intuition) and the basic subtractor $$\vert\hat{S}\vert = \vert Y\vert - \alpha \widehat{\vert N\vert}$$.
- **25–40 min** — Over-subtraction $$\alpha$$, spectral floor $$\beta$$, and a worked numerical example on a few bins.
- **40–50 min** — Musical noise: mechanism, listening checklist, and SpeexDSP preprocessor as a production pointer.
- **50–60 min** — Pitfalls, exercises, and when subtraction is still a front-end before DeepFilterNet-class models.

## Core explanation

### Mixture model and STFT magnitudes

Assume a single-channel observation

$$
y[t] = s[t] + n[t],
$$

where $$s$$ is speech and $$n$$ is additive noise. After a windowed STFT (Chapter 02), write complex spectra $$Y(k,\ell)$$, $$S(k,\ell)$$, $$N(k,\ell)$$ for frequency bin $$k$$ and frame $$\ell$$. Under approximate additivity of complex STFT bins (true when the analysis window is long enough relative to impulse responses of interest),

$$
Y(k,\ell) = S(k,\ell) + N(k,\ell).
$$

Classical spectral subtraction works on **magnitudes** (or powers) and reuses the **noisy phase**:

$$
\hat{S}(k,\ell) = \bigl(\vert Y(k,\ell)\vert - \widehat{\vert N\vert}(k,\ell)\bigr)_{+} \; e^{j\angle Y(k,\ell)}.
$$

The positive-part $$(\cdot)_{+}$$ prevents negative magnitudes. Power-domain variants subtract estimated noise power from $$\vert Y\vert^2$$ and take a square root—same philosophy, different bias/variance trade-offs.

### Noise floor estimation (assumptions)

You need $$\widehat{\vert N\vert}(k)$$. Common teaching assumptions:

1. **Stationary noise during an initial silence** — average magnitudes over the first $$L_0$$ frames assumed to be noise-only.
2. **Voice-activity detection (VAD)** — update the noise estimate only when speech is absent.
3. **Min-statistics / recursive tracking** — track a smoothed minimum of the noisy spectrum (used widely in classical literature and in SpeexDSP-style preprocessors).

A simple recursive update during non-speech frames is

$$
\widehat{\vert N\vert}(k,\ell) = \lambda \widehat{\vert N\vert}(k,\ell-1) + (1-\lambda)\,\vert Y(k,\ell)\vert,
$$

with smoothing factor $$\lambda \in (0,1)$$ close to 1 for slow adaptation.

**Critical assumption:** if noise is non-stationary (keyboard clicks, competing talkers, music), a slowly adapted floor under-subtracts during bursts and over-subtracts afterward. That is the main reason pure subtraction fails in modern VoIP scenarios with highly non-stationary backgrounds.

### Over-subtraction and spectral flooring

Boll’s original idea and the Berouti-style refinements introduce two controls:

- **Over-subtraction factor** $$\alpha \ge 1$$ — subtract *more* than the estimated noise to reduce residual peaks.
- **Spectral floor** $$\beta \in (0,1)$$ — never let the magnitude fall below $$\beta\,\vert Y\vert$$ (or $$\beta\,\widehat{\vert N\vert}$$), which reduces musical noise at the cost of leaving some residual noise.

A practical magnitude rule is

$$
\vert\hat{S}(k,\ell)\vert = \max\bigl(\vert Y(k,\ell)\vert - \alpha\,\widehat{\vert N\vert}(k,\ell),\; \beta\,\vert Y(k,\ell)\vert\bigr).
$$

Sometimes $$\alpha$$ itself is SNR-dependent: larger $$\alpha$$ at low a priori SNR, smaller $$\alpha$$ when speech dominates. That heuristic already points toward **Wiener filtering** (next lesson), which chooses a continuous gain from an SNR estimate rather than a hard subtract-and-floor.

### Pseudocode (magnitude STFT)

```text
for each frame ell:
  Y = STFT_frame(y_ell)           # complex
  magY = |Y|
  if is_noise_frame(ell):
      Nhat = λ * Nhat + (1-λ) * magY
  magS = max(magY - α * Nhat, β * magY)
  S_hat = magS * exp(j * angle(Y))
  emit ISTFT_OLA(S_hat)
```

Keep hop, window, and overlap-add consistent with Chapter 02 so that perfect reconstruction holds when $$\alpha=0$$ and $$\beta=1$$ (identity gain).

### Musical noise: what you hear and why

After subtraction, bins where the noise estimate was slightly **too low** leave thin residual peaks; bins where it was **too high** dig holes. Over frames, those residual peaks wander in frequency and sound like random tones or “birds”—hence **musical noise**. Flooring and temporal smoothing of the gain reduce the artifact; aggressive $$\alpha$$ without flooring makes it worse.

**Listening checklist (30 seconds per clip):**

1. Play noisy input and subtractor output at matched loudness.
2. Solo a noise-only region: do you hear chirps / whistling?
3. Solo a low-SNR speech region: is speech hollow or robotic?
4. Toggle $$\beta$$ up: musical noise should drop; residual broadband noise should rise.
5. Toggle $$\alpha$$ up: noise drops; speech distortion and musical tones often rise.

## Worked example (toy bins)

Suppose one frame, three bins, magnitudes $$\vert Y\vert = [5.0,\; 2.0,\; 1.2]$$, noise estimate $$\widehat{\vert N\vert} = [1.0,\; 1.5,\; 1.0]$$, $$\alpha=1.5$$, $$\beta=0.1$$.

- **Bin 0:** $$5.0 - 1.5\cdot 1.0 = 3.5$$, floor $$0.1 \cdot 5.0 = 0.5$$ → **$$3.5$$** (passes speech).
- **Bin 1:** $$2.0 - 1.5\cdot 1.5 = -0.25$$, floor $$0.1 \cdot 2.0 = 0.2$$ → **$$0.2$$** (floored).
- **Bin 2:** $$1.2 - 1.5\cdot 1.0 = -0.30$$, floor $$0.1 \cdot 1.2 = 0.12$$ → **$$0.12$$** (floored).

Bins 1–2 illustrate why flooring matters: without it you would clip to zero and create hard spectral holes that become musical after ISTFT.

---

### Deep-Dive Explanation: How Random Noise Fluctuations Turn into “Musical Birdies” (Read Slowly)

#### Step 1: The noise spectrum is a random variable, not a flat constant
Even for pure stationary white noise with mean magnitude $$\widehat{\vert N\vert} = 1.0$$, the actual magnitude in each STFT bin fluctuates randomly from frame to frame (following a Rayleigh distribution): some bins dip to $$0.4$$ while neighboring bins spike to $$2.1$$!

#### Step 2: Hard half-wave rectification isolates random single-bin spikes
When you subtract $$\widehat{\vert N\vert} = 1.0$$ and clip negatives to $$0$$, all the $$0.4$$ bins become **exact silence ($$0.0$$)** while the occasional $$2.1$$ bin survives as an isolated narrow spike ($$1.1$$) surrounded by zeros. An isolated spike in frequency is a **pure sine tone** in time—lasting one 20 ms frame!

#### Step 3: Frame-to-frame wandering creates chirping “musical noise”
On the next hop, a *different* random bin spikes above $$1.0$$, producing a short tone at a different pitch. Our ears perceive that rapid succession of random 20 ms sine bursts as metallic whistling or underwater chirping. Raising $$\beta$$ (e.g., $$0.1$$) masks those isolated spikes in a soft broadband floor—and motivates the smooth continuous gains of Wiener filtering (Lesson 03-02).

Summary of the spectral subtraction recipe:

$$
\vert \hat{S}(k,\ell)\vert = \max\!\bigl(\vert Y(k,\ell)\vert - \alpha\,\widehat{\vert N\vert}(k,\ell),\; \beta\,\vert Y(k,\ell)\vert\bigr)
\;\xrightarrow{\times e^{j\angle Y}}\;
\text{ISTFT / OLA}.
$$

## When classical subtraction still appears as a front-end

- **Very cheap always-on gate** on embedded DSPs before a heavier neural stage.
- **Noise-floor bootstrap** to initialize a priori SNR for Wiener / MMSE estimators.
- **SpeexDSP preprocessor** and similar VoIP stacks: spectral subtraction / noise gating as part of a broader AGC + VAD + NS chain.
- **Hybrid pipelines** where a classical block removes stationary HVAC hum and a neural model cleans residual non-stationary noise (see Chapter 04 hybrids).

For Mezon-class full-band real-time NS, subtraction alone is not enough—but understanding it makes DeepFilterNet’s “learned filter / mask” behavior much less mysterious. The left panel of the figure is this rule in the power domain: blue bars are $$\vert Y\vert^2$$, the orange line is the noise floor, and the green bars are what survives the floor. The right panel is not subtraction; it is the soft Wiener gain of the next lesson.

## Pitfalls

- Treating power and magnitude formulas as interchangeable without adjusting $$\alpha,\beta$$.
- Updating the noise estimate during speech → **speech erasure**.
- Setting $$\beta=0$$ “to remove all noise” → severe musical noise.
- Ignoring OLA window normalization → gain errors that sound like pumping.
- Expecting subtraction to fix echo (that is AEC, lesson 03-04) or directional interferers (beamforming, 03-05).

## Mini-lab

**Goal.** Run magnitude spectral subtraction on eight bins and print which bins hit the floor.

```python
import numpy as np

magY = np.array([1.2, 3.5, 0.8, 4.0, 2.2, 1.1, 0.5, 2.8])
Nhat = np.array([1.0, 1.0, 0.9, 1.1, 1.0, 0.8, 0.7, 1.0])
alpha, beta = 2.0, 0.1
raw = magY - alpha * Nhat
magS = np.maximum(raw, beta * magY)
clipped = np.where(raw < beta * magY)[0]
print("raw", np.round(raw, 2))
print("magS", np.round(magS, 2))
print("clipped bins", clipped.tolist())
```

**Expected.** `raw` is `[-0.8, 1.5, -1.0, 1.8, 0.2, -0.5, -0.9, 0.8]`. After the floor, `magS` is `[0.12, 1.5, 0.08, 1.8, 0.22, 0.11, 0.05, 0.8]`. Clipped bins are `[0, 2, 4, 5, 6]`. Bins 1, 3, and 7 pass through unclipped.

**Failure modes.** Using power $$\vert Y\vert^2$$ with these magnitude numbers, or forgetting `beta * magY`, changes both the clipped set and the floor values. A clip test written as `raw < 0` misses bin 4, where the raw remainder is positive but still under the floor. `alpha=1` clips fewer bins and hides the over-subtraction the example is about.

## Exercises

1. **Derive the floor case.** Show that if $$\vert Y\vert < \alpha\widehat{\vert N\vert}$$, the floored rule returns $$\beta\vert Y\vert$$. Interpret $$\beta$$ as a residual noise fraction.
2. **Implement (offline).** In Python/NumPy, run magnitude spectral subtraction on a 16 kHz clip with a known stationary noise. Sweep $$\alpha\in\{1.0,1.5,2.0\}$$ and $$\beta\in\{0.01,0.1,0.2\}$$; note musical noise vs residual noise.
3. **Non-stationary stress test.** Replace stationary noise with keyboard bursts. Explain why a fixed $$\widehat{\vert N\vert}$$ fails; propose a VAD-gated update rule.
4. **Product judgment.** Write five bullets arguing when you would keep SpeexDSP-style subtraction as a pre-stage in front of a DeepFilterNet3 WASM path versus disabling it entirely.

### Answer hints

1. The `max` returns the second argument exactly when the first is smaller; $$\beta\vert Y\vert$$ is a fraction of the noisy magnitude you refuse to erase.
2. Hold the noise estimate fixed from a leading noise-only region, then listen to noise-only tails as $$\alpha$$ grows and $$\beta$$ shrinks.
3. A burst above the frozen floor is under-subtracted; the frames after it are over-subtracted. Update $$\widehat{\vert N\vert}$$ only when a VAD says noise.
4. Keep a cheap stationary front-end when the neural model is the expensive stage and the hum is steady; disable it when it already punches holes that the 48 kHz model then treats as speech structure.

## Further reading

- S. F. Boll, “Suppression of acoustic noise in speech using spectral subtraction,” *IEEE Trans. Acoust., Speech, Signal Process.*, 1979 (classic formulation).
- M. Berouti, R. Schwartz, J. Makhoul — over-subtraction / spectral floor refinements (cite by name; standard textbook treatment in Loizou, *Speech Enhancement*).
- SpeexDSP preprocessor documentation (Xiph) — production classical NS pointer.
- Contrast next: Ephraim–Malah / Wiener estimators (lesson 03-02) and RNNoise’s hybrid design (lesson 04-06).

## Video tham khảo

- [Spectral Subtraction In Python - Alexx Mitchell](https://www.youtube.com/watch?v=Xb--68NlxS0) — The Audio Programmer, English. **xem trước.** Watch the algorithm diagram: estimate a noise magnitude, subtract, and floor. Musical noise is what a negative bin becomes if the floor is naive.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, English. Use the opening to hear why a product eventually replaced this classical suppressor, after you can implement it.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, English. Listen after the diagram. The demo is a later suppressor, useful as the sound spectral subtraction is trying and failing to reach.
