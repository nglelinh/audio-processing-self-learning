---
layout: post
title: "03-05 Beamforming / GSC / IVA as front-ends"
chapter: "03"
order: 5
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter03
lesson_type: required
draft: false
---

With a single microphone, two people talking at equal loudness in a café are nearly impossible to tell apart—their voices overlap in the exact same frequency bands. Add a **second microphone** just 2 centimeters away, and physics hands you a brand-new dimension: **space**. A sound coming from $$45^\circ$$ off-axis hits one mic $$41.2\,\mu\mathrm{s}$$ (nearly 2 samples at 48 kHz) later than the other!

**Beamforming**, the **Generalized Sidelobe Canceller (GSC)**, and **Independent Vector Analysis (IVA)** turn those tiny inter-mic time delays into a directional acoustic spotlight—suppressing off-axis interferers *before* handing a cleaner mono stream to a neural enhancer like DeepFilterNet. This lesson closes Chapter 03 by mapping multi-mic spatial front-ends and showing exactly where they plug into a mono product pipeline.

![LiveKit publish path through a single-channel DeepFilterNoiseFilterProcessor, the stage a beamformer would have to feed]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. This is the mono publish path; a beamformer is not drawn, and would sit in front of DeepFilterNoiseFilterProcessor so the processor still sees one channel.*

**Lesson roadmap:** Background Knowledge Map (steering vectors & time-of-arrival geometry, fixed vs. adaptive beamforming, blind separation via IVA) → Delay-and-sum, MVDR, GSC, and IVA architectures → Hybrid spatial + mono neural patterns → Worked example: computing the exact $$41.2\,\mu\mathrm{s}$$ (1.98-sample) inter-mic delay and phase shift for a 2 cm dual-mic array at 48 kHz → Deep-Dive Explanation (Read Slowly): 3 steps from delay-and-sum to MVDR/GSC and hybrid neural postfiltering → Decision checklist, Pitfalls, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: Multi-Microphone Spatial Audio Processing

### 1. Steering Vectors — Encoding Direction as Phase Shifts
When a plane wave from angle $$\theta$$ crosses a microphone array with spacing $$d$$, the arrival delay $$\tau = (d\sin\theta)/c$$ turns into a frequency-dependent phase shift $$e^{-j2\pi f\tau}$$ in the STFT domain. Stacking those phase factors across all $$M$$ mics produces the **steering vector** $$\mathbf{a}(\theta, f)$$.

### 2. Fixed vs. Adaptive Beamforming (Delay-and-Sum, MVDR, GSC)
- **Delay-and-sum** aligns the target’s phases and averages—boosting target SNR against diffuse noise by up to $$M\times$$ in power.
- **MVDR / GSC** goes further by steering sharp **spatial nulls** straight at loud directional interferers while constraining the target direction to unity gain ($$\mathbf{w}^H\mathbf{a} = 1$$).

### 3. Blind Separation (IVA) and Hybrid Spatial + Neural Front-Ends
When you do *not* know the array geometry or talker angle, **Independent Vector Analysis (IVA)** separates sources purely via statistical independence across microphones. In production, a spatial front-end collapses $$M$$ mics down to **1 cleaner mono channel**, letting you reuse an unmodified mono DeepFilterNet3 model downstream!

---

## Learning objectives

You will explain delay-and-sum and MVDR goals in plain language, sketch a GSC (fixed beamformer + blocking matrix + adaptive canceler), summarize IVA as a blind multi-channel separator, and decide when a spatial front-end plus mono DeepFilterNet-class model beats mono-only NS.

## 60-minute teaching plan

- **0–10 min** — Two-mic laptop demo narrative: target talker vs interferer direction.
- **10–25 min** — Steering vectors, delay-and-sum, MVDR objective sketch.
- **25–40 min** — GSC structure; what the adaptive branch cancels.
- **40–50 min** — IVA / BSS pointer; hybrid front-end + neural refine.
- **50–60 min** — Pitfalls, exercises, product reality check (most Mezon paths are still mono).

## Core explanation

### Spatial model (far-field sketch)

For microphone $$m=1\ldots M$$, a plane-wave target from direction $$\theta$$ at frequency $$f$$ has relative phase shifts encoded in a **steering vector** $$\mathbf{a}(\theta,f)$$. The stacked spectrum is

$$
\mathbf{y}(f,\ell) = \mathbf{a}(\theta,f)\,S(f,\ell) + \mathbf{v}(f,\ell),
$$

with $$\mathbf{v}$$ containing noise and interferers. A beamformer applies weights $$\mathbf{w}(f)$$:

$$
Z(f,\ell) = \mathbf{w}^H(f)\,\mathbf{y}(f,\ell).
$$

### Delay-and-sum

Choose delays (phases) so the target aligns coherently across mics, then average. Gain against **incoherent** noise scales with $$M$$, but **coherent interferers** from other directions are only partially attenuated. It is the simplest teaching beamformer and a fine baseline.

### MVDR cartoon (minimum variance distortionless response)

Solve: minimize output power subject to unity gain toward the target,

$$
\min_{\mathbf{w}} \mathbf{w}^H \mathbf{R}_{yy}\mathbf{w} \quad \text{s.t.} \quad \mathbf{w}^H\mathbf{a}=1.
$$

The closed form $$\mathbf{w}\propto \mathbf{R}_{yy}^{-1}\mathbf{a}$$ (normalized) steers a null toward interferers while keeping the target. Estimating $$\mathbf{R}_{yy}$$ (or a noise-only $$\mathbf{R}_{nn}$$) robustly is the hard engineering part—steering error and RTF mismatch cause target cancellation (self-nulling).

### GSC — generalized sidelobe canceller

GSC reparameterizes beamforming into:

1. **Fixed beamformer (FBF)** — looks at the target (delay-and-sum / MVDR fixed weights).
2. **Blocking matrix (BM)** — projects away the target so outputs are “target-free” noise references.
3. **Adaptive noise canceler** — NLMS/RLS filters subtract interference estimated from BM channels from the FBF output.

```text
 mics → Fixed beamformer ───────────────────────────→ + → out
     └→ Blocking matrix → Adaptive filters → (−)
```

**Why engineers like GSC:** unconstrained adaptive filtering on the noise references; easy to add voice-activity control so the adaptive path freezes during target speech.

### IVA / blind spatial separation (pointer)

**Independent vector analysis (IVA)** and related BSS methods separate sources from multi-mic mixtures without an explicit steering vector, using statistical independence across frequency-grouped vectors. Teaching level:

- Treat IVA as a **blind spatial front-end** that yields a coarse target estimate + interferer estimate.
- A lightweight neural model (e.g. GTCRN-class) can refine the IVA output—hybrid papers on dual-channel low-SNR SE follow this pattern.

You do not need to derive IVA contrast functions here; you need to know it exists as a classical multi-channel tool and that hybrids use it when DOA is unknown.

### Hybrid front-end + neural mono enhancer

Pattern A — **GSC → DeepFilterNet2**: spatial cancel of strong directional ego-noise (drone rotors, fan), then DF2 cleans residual diffuse noise.  
Pattern B — **IVA → GTCRN**: blind separation then tiny CRN refine.  
Pattern C — **mono DF3 only**: correct default when $$M=1$$ (most browser tabs).

**Mezon product note:** current npm / WASM paths are typically **mono**. Multi-mic is a stretch goal—learn the front-ends so you can design a future native pipeline without rewriting the neural core. A beamformer would be a spatial pre-filter in front of that mono processor: several microphones in, one channel out, and only then the per-bin gain of a single-channel suppressor. The figure above is the single-channel product path. It does not contain a beamformer; the honest reading is where a beamformer would have to sit, which is upstream of `DeepFilterNoiseFilterProcessor`.

---

### Deep-Dive Explanation: How Two Microphones 2 cm Apart Steer a Spatial Null (Read Slowly)

#### Step 1: Compute the physical delay $$\tau$$ and phase shift by hand
Place two mics $$d = 0.02\,\mathrm{m}$$ apart (speed of sound $$c = 343\,\mathrm{m/s}$$):
- **Broadside target ($$\theta = 0^\circ$$, straight ahead):** $$\tau = 0\,\mu\mathrm{s}$$ (0 samples). Both mics hear the target identically: $$\mathbf{a}(0^\circ, f) = [1, 1]^T$$.
- **Off-axis interferer ($$\theta = 45^\circ$$):** $$\tau = \frac{0.02 \sin 45^\circ}{343} \approx 41.2\,\mu\mathrm{s}$$, which is $$41.2\times 10^{-6} \times 48000 \approx 1.98$$ samples at 48 kHz! At $$f = 2\,\mathrm{kHz}$$, that delay creates a phase difference of $$2\pi f\tau \approx 0.52\,\mathrm{rad}$$ ($$\approx 30^\circ$$).

#### Step 2: Watch the GSC Blocking Matrix turn the target into zero
For a broadside target ($$y_1 = s + v_1,\; y_2 = s + v_2$$), the **Fixed Beamformer** sums $$\frac{1}{2}(y_1 + y_2) = s + \frac{1}{2}(v_1 + v_2)$$ while the **Blocking Matrix** subtracts $$y_1 - y_2 = v_1 - v_2$$—canceling $$s$$ completely and producing a pure noise reference for the adaptive filter!

#### Step 3: Hand the single spatially cleaned stream to a mono neural enhancer
Because beamforming cannot easily cancel diffuse reverberant noise (arriving from *all* angles at once), pairing **GSC/MVDR → Mono DeepFilterNet** gives you the best of both worlds: geometry kills directional babble, and the neural postfilter erases remaining diffuse hiss!

Summary of the multi-mic hybrid pipeline:

$$
\mathbf{y}_M\ (M \ge 2\text{ mics})
\;\xrightarrow{\text{Delay-and-sum / GSC / IVA}}\;
z_{\text{mono}}
\;\xrightarrow{\text{Mono Neural NS (DF3)}}\;
\hat{s}_{\text{clean}}.
$$

## Decision checklist

- $$M=1$$ → classical / neural mono NS (Ch. 03–04); skip beamforming.
- $$M\ge 2$$, known target direction, strong directional noise → GSC / MVDR front-end.
- $$M\ge 2$$, unknown geometry / moving talkers → IVA / robust adaptive BF, then neural.
- CPU budget tiny → prefer simple delay-and-sum + ultra-light NS over full IVA.
- Browser getUserMedia often exposes mono after OS processing—verify actual channel count.

## Pitfalls

- Steering vector mismatch → **target cancellation** (sounds like NS over-suppressing speech).
- Adapting GSC during target activity without a VAD → speech leakage into BM path.
- Assuming stereo laptop mics have calibrated geometry (they often do not).
- Running multi-channel STFT with inconsistent channel delays (USB clocking).
- Expecting beamforming to fix **echo** without a far-end reference—still need AEC.

## Mini-lab

**Goal.** Far-field delay between two microphones 2 cm apart, at broadside and at 45°.

```python
import numpy as np

d, c, fs = 0.02, 343.0, 48000  # meters, m/s, Hz
for deg in (0, 45):
    tau = d * np.sin(np.deg2rad(deg)) / c
    print(deg, "deg", round(tau * 1e6, 1), "us", round(tau * fs, 2), "samples")
```

**Expected.** Broadside: `0.0 µs`, `0.0` samples. At 45°: about `41.2 µs`, about `1.98` samples at 48 kHz. Delay-and-sum at 48 kHz is a fractional-sample shift, not a multi-tap “room” filter.

**Failure modes.** Using degrees in `np.sin` without converting to radians gives a nonsense delay (the 45° case will not be ~2 samples). Forgetting $$\sin\theta$$ and using $$d/c$$ for every angle makes broadside look like endfire. A 16 kHz print of “samples” is about 0.66 at 45°, so a hardcoded 48 kHz assumption has to be visible in the script.

## Exercises

1. **Delay-and-sum.** For 2 mics spaced $$d=2\,\mathrm{cm}$$, $$f=2\,\mathrm{kHz}$$, speed of sound $$343\,\mathrm{m/s}$$, compute the inter-mic delay for broadside vs 45° incidence (far-field).
2. **GSC sketch.** Label FBF, BM, adaptive filters on a diagram; mark where a neural postfilter would attach.
3. **Product brief.** One page: propose a dual-mic native mode for Mezon that reuses the existing mono DF3 ONNX and adds a delay-and-sum front-end only.
4. **Reading map.** Skim one hybrid abstract (GSC+DeepFilterNet2 or IVA+GTCRN); write three bullets on what the classical stage contributes vs the neural stage.

### Answer hints

1. Broadside delay is 0. At 45°, $$\tau=d\sin\theta/c$$ is about 41 µs, roughly two samples at 48 kHz.
2. Neural postfilter attaches to the GSC output, after the adaptive subtraction, on a single channel.
3. Delay-and-sum emits one waveform; the existing mono ONNX does not grow a second input.
4. The classical stage uses the extra microphone (nulls or independence). The neural stage is still a single-channel enhancer on whatever that spatial stage passed through.

## Further reading

- Van Trees, *Optimum Array Processing* — MVDR / beamforming foundations.
- Griffiths & Jim — generalized sidelobe canceller (classic GSC).
- WebRTC / mobile multi-mic AEC+BF engineering notes (platform docs).
- Survey hybrids: GSC–DeepFilterNet2 (drone ego-noise), IVA+GTCRN dual-channel SE (name-level pointers).
- DeepFilterNet2 paper — mono neural stage often used *after* classical spatial cleaning.

## Video tham khảo

- [What is Beamforming? ("the best explanation I’ve ever heard")](https://www.youtube.com/watch?v=A1n5Hhwtz78) — Iain Explains Signals, Systems, and Digital Comms, English. **xem trước.** Watch the delay that lines up one direction before the sum. Delay-and-sum is the front-end geometry this lesson starts from; GSC and IVA are what you reach for when that sum is not enough.
