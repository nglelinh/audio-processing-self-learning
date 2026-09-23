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

Spectral subtraction is the classical doorway into noise suppression: estimate a noise magnitude spectrum, subtract it from the noisy speech spectrum, and rebuild the waveform. It is simple enough to implement in an afternoon, yet rich enough to teach every artifact—especially *musical noise*—that modern neural systems still try to avoid. This lesson builds the magnitude-STFT recipe, the over-subtraction / spectral-floor heuristics used in production preprocessors (including SpeexDSP-style pipelines), and a clear map of when subtraction still appears as a cheap front-end before a neural enhancer.

## Learning objectives

By the end of this lesson you will be able to state the additive mixture model in the STFT domain, write magnitude spectral subtraction with over-subtraction and flooring in pseudocode, explain why residual peaks sound like musical tones, and decide when a classical subtractor is a useful pre-stage versus when you should jump straight to a Wiener or neural masker.

## 60-minute teaching plan

- **0–10 min** — Additive model $$Y = S + N$$, magnitude vs power spectra, and why phase is usually kept from the noisy frame.
- **10–25 min** — Noise estimation (VAD / min-statistics intuition) and the basic subtractor $$|\hat{S}| = |Y| - \alpha |\hat{N}|$$.
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
\hat{S}(k,\ell) = \bigl(|Y(k,\ell)| - \widehat{|N|}(k,\ell)\bigr)_{+} \; e^{j\angle Y(k,\ell)}.
$$

The positive-part $$(\cdot)_{+}$$ prevents negative magnitudes. Power-domain variants subtract estimated noise power from $$|Y|^2$$ and take a square root—same philosophy, different bias/variance trade-offs.

### Noise floor estimation (assumptions)

You need $$\widehat{|N|}(k)$$. Common teaching assumptions:

1. **Stationary noise during an initial silence** — average magnitudes over the first $$L_0$$ frames assumed to be noise-only.
2. **Voice-activity detection (VAD)** — update the noise estimate only when speech is absent.
3. **Min-statistics / recursive tracking** — track a smoothed minimum of the noisy spectrum (used widely in classical literature and in SpeexDSP-style preprocessors).

A simple recursive update during non-speech frames is

$$
\widehat{|N|}(k,\ell) = \lambda \widehat{|N|}(k,\ell-1) + (1-\lambda)\,|Y(k,\ell)|,
$$

with smoothing factor $$\lambda \in (0,1)$$ close to 1 for slow adaptation.

**Critical assumption:** if noise is non-stationary (keyboard clicks, competing talkers, music), a slowly adapted floor under-subtracts during bursts and over-subtracts afterward. That is the main reason pure subtraction fails in modern VoIP scenarios with highly non-stationary backgrounds.

### Over-subtraction and spectral flooring

Boll’s original idea and the Berouti-style refinements introduce two controls:

- **Over-subtraction factor** $$\alpha \ge 1$$ — subtract *more* than the estimated noise to reduce residual peaks.
- **Spectral floor** $$\beta \in (0,1)$$ — never let the magnitude fall below $$\beta\,|Y|$$ (or $$\beta\,\widehat{|N|}$$), which reduces musical noise at the cost of leaving some residual noise.

A practical magnitude rule is

$$
|\hat{S}(k,\ell)| = \max\bigl(|Y(k,\ell)| - \alpha\,\widehat{|N|}(k,\ell),\; \beta\,|Y(k,\ell)|\bigr).
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

Suppose one frame, three bins, magnitudes $$|Y| = [5.0,\; 2.0,\; 1.2]$$, noise estimate $$\widehat{|N|} = [1.0,\; 1.5,\; 1.0]$$, $$\alpha=1.5$$, $$\beta=0.1$$.

Bin 0: $$5.0 - 1.5\cdot 1.0 = 3.5$$, floor $$0.5$$ → $$3.5$$.  
Bin 1: $$2.0 - 1.5\cdot 1.5 = -0.25$$ → floor $$0.2$$ → $$0.2$$.  
Bin 2: $$1.2 - 1.5\cdot 1.0 = -0.3$$ → floor $$0.12$$ → $$0.12$$.

Bins 1–2 illustrate why flooring matters: without it you would clip to zero and create hard spectral holes that become musical after ISTFT.

## When classical subtraction still appears as a front-end

- **Very cheap always-on gate** on embedded DSPs before a heavier neural stage.
- **Noise-floor bootstrap** to initialize a priori SNR for Wiener / MMSE estimators.
- **SpeexDSP preprocessor** and similar VoIP stacks: spectral subtraction / noise gating as part of a broader AGC + VAD + NS chain.
- **Hybrid pipelines** where a classical block removes stationary HVAC hum and a neural model cleans residual non-stationary noise (see Chapter 04 hybrids).

For Mezon-class full-band real-time NS, subtraction alone is not enough—but understanding it makes DeepFilterNet’s “learned filter / mask” behavior much less mysterious.

## Pitfalls

- Treating power and magnitude formulas as interchangeable without adjusting $$\alpha,\beta$$.
- Updating the noise estimate during speech → **speech erasure**.
- Setting $$\beta=0$$ “to remove all noise” → severe musical noise.
- Ignoring OLA window normalization → gain errors that sound like pumping.
- Expecting subtraction to fix echo (that is AEC, lesson 03-04) or directional interferers (beamforming, 03-05).

## Exercises

1. **Derive the floor case.** Show that if $$|Y| < \alpha\widehat{|N|}$$, the floored rule returns $$\beta|Y|$$. Interpret $$\beta$$ as a residual noise fraction.
2. **Implement (offline).** In Python/NumPy, run magnitude spectral subtraction on a 16 kHz clip with a known stationary noise. Sweep $$\alpha\in\{1.0,1.5,2.0\}$$ and $$\beta\in\{0.01,0.1,0.2\}$$; note musical noise vs residual noise.
3. **Non-stationary stress test.** Replace stationary noise with keyboard bursts. Explain why a fixed $$\widehat{|N|}$$ fails; propose a VAD-gated update rule.
4. **Product judgment.** Write five bullets arguing when you would keep SpeexDSP-style subtraction as a pre-stage in front of a DeepFilterNet3 WASM path versus disabling it entirely.

## Further reading

- S. F. Boll, “Suppression of acoustic noise in speech using spectral subtraction,” *IEEE Trans. Acoust., Speech, Signal Process.*, 1979 (classic formulation).
- M. Berouti, R. Schwartz, J. Makhoul — over-subtraction / spectral floor refinements (cite by name; standard textbook treatment in Loizou, *Speech Enhancement*).
- SpeexDSP preprocessor documentation (Xiph) — production classical NS pointer.
- Contrast next: Ephraim–Malah / Wiener estimators (lesson 03-02) and RNNoise’s hybrid design (lesson 04-06).
