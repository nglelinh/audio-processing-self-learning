---
layout: post
title: "03-02 Wiener filtering for speech"
chapter: "03"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter03
lesson_type: required
draft: false
---

Where spectral subtraction decides “subtract then floor,” the **Wiener filter** decides a continuous gain per bin from an estimated signal-to-noise ratio. The right-hand curve in the figure is that gain; the left-hand bars are the subtractor it replaces.

![Wiener gain versus a priori SNR, beside the spectral-subtraction bars it softens]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Figure. The Wiener gain is \(1/2\) (\(-6\,\mathrm{dB}\)) when speech and noise power are equal, and it never becomes the hard holes of the subtraction bars on the left.*

It is the analytical bridge between classical subtractors and modern mask-based neural enhancers: DeepFilterNet-style models can be read as learned, data-driven cousins of time–frequency Wiener gains, with far richer features and multi-frame filters. This lesson develops the MMSE intuition, a priori / a posteriori SNR, decision-directed tracking, and practical speech Wiener variants used in VoIP stacks.

## Learning objectives

You will derive the frequency-domain Wiener gain $$G = \xi/(1+\xi)$$ from an MMSE argument under Gaussian assumptions, distinguish a priori SNR $$\xi$$ from a posteriori SNR $$\gamma$$, implement a decision-directed tracker at pseudocode level, and explain how Wiener gains relate to soft masks in neural speech enhancement.

## 60-minute teaching plan

- **0–10 min** — From hard subtraction to soft gains; listen to a Wiener vs subtractor demo narrative.
- **10–25 min** — MMSE derivation sketch → $$G^{\mathrm{Wiener}}(k)=\xi/(\xi+1)$$.
- **25–40 min** — Estimating $$\xi$$ and $$\gamma$$; decision-directed recursion (Ephraim–Malah style).
- **40–50 min** — Speech-specific tricks: flooring the gain, bias toward noise reduction, link to SpeexDSP / WebRTC NS.
- **50–60 min** — Pitfalls, exercises, preview of Kalman tracking (03-03).

## Core explanation

### Wiener gain in one line

For an additive model $$Y=S+N$$ in a given STFT bin (drop $$(k,\ell)$$), the **linear MMSE estimator** of $$S$$ given $$Y$$ under uncorrelated zero-mean Gaussian assumptions is multiplication by

$$
G^{\mathrm{W}} = \frac{P_S}{P_S + P_N} = \frac{\xi}{\xi + 1},
$$

where $$P_S=\mathbb{E}|S|^2$$, $$P_N=\mathbb{E}|N|^2$$, and the **a priori SNR** is

$$
\xi = \frac{P_S}{P_N}.
$$

The enhanced spectrum is $$\hat{S} = G^{\mathrm{W}} Y$$ (complex multiply—phase of $$Y$$ preserved automatically).

**Interpretation:** if speech power ≫ noise power ($$\xi\to\infty$$), $$G\to 1$$ (pass-through). If noise dominates ($$\xi\to 0$$), $$G\to 0$$ (suppress). Between those extremes the gain is a smooth soft mask—exactly the shape neural mask estimators rediscover from data.

### A posteriori SNR

The **a posteriori SNR** uses the *observed* power:

$$
\gamma = \frac{|Y|^2}{P_N}.
$$

If $$P_N$$ is known, $$\gamma$$ is measurable each frame; $$\xi$$ is not, because $$P_S$$ is unknown. Classical speech enhancement spends most of its ingenuity on estimating $$\xi$$.

A useful identity under the model is $$\mathbb{E}[\gamma]=\xi+1$$, so a naive plug-in is $$\hat{\xi}=\gamma-1$$ clipped at zero—the **ML estimate**—but it is noisy frame-to-frame and produces musical artifacts similar to aggressive subtraction.

### Decision-directed a priori SNR (Ephraim–Malah)

The celebrated **decision-directed** approach recursively blends a prediction from the previous enhanced frame with the instantaneous ML estimate:

$$
\hat{\xi}(\ell) = \eta\,\frac{|G(\ell-1) Y(\ell-1)|^2}{P_N} + (1-\eta)\,\max\bigl(\gamma(\ell)-1,\,0\bigr),
$$

with $$\eta$$ typically $$0.98$$. Then set

$$
G(\ell) = \frac{\hat{\xi}(\ell)}{\hat{\xi}(\ell)+1}.
$$

High $$\eta$$ yields smooth gains (less musical noise, more reverberant / smeared speech). Low $$\eta$$ tracks non-stationary noise better but sounds twitchy.

### Power spectra and noise estimation

You still need $$P_N(k,\ell)$$. Reuse the noise trackers from spectral subtraction (VAD-gated recursive mean, min-statistics). Many VoIP preprocessors combine:

1. Noise PSD tracker,
2. Decision-directed $$\xi$$,
3. Wiener or Ephraim–Malah MMSE gain,
4. Optional residual echo / AGC stages (Chapter 03-04).

### Soft mask view (bridge to Chapter 04)

Define an ideal ratio mask (IRM) in power domain:

$$
M^{\mathrm{IRM}} = \frac{|S|^2}{|S|^2 + |N|^2} = \frac{\xi}{\xi+1}.
$$

That is *exactly* the Wiener gain when $$\xi$$ is the true a priori SNR. Neural SE models often regress a mask $$\hat{M}$$ toward IRM / ideal binary mask / complex ideal ratio mask targets. Reading DeepFilterNet as “learned multi-frame filtering + ERB-band gains” is easier once Wiener is in your bones: the classical formula is the closed-form optimum under strong assumptions; the network relaxes those assumptions using data.

### Pseudocode

```text
for each frame ell:
  Y = STFT(y_ell)
  γ = |Y|^2 / P_N
  ξ = η * |S_prev|^2 / P_N + (1-η) * max(γ - 1, 0)
  G = ξ / (ξ + 1)
  G = max(G, G_min)          # gain floor, e.g. -20 dB
  S_hat = G * Y
  S_prev = S_hat
  emit ISTFT_OLA(S_hat)
  update P_N if noise-only
```

## Worked checklist: tuning a speech Wiener

| Knob | Increase → effect | Decrease → effect |
|------|-------------------|-------------------|
| $$\eta$$ | smoother, less musical | faster, twitchier |
| $$G_{\min}$$ | more residual noise | more distortion / holes |
| Noise update rate | tracks non-stationary noise | stabler during speech |
| Frame / hop | latency vs resolution (Ch. 02) | — |

**Sanity check:** with $$P_N\to 0$$, $$G$$ should approach 1 and the output should match the input (OLA-perfect). Unit-test that path before shipping.

## Pitfalls

- Using $$\gamma/(\gamma+1)$$ as if it were Wiener— that is a different (worse) plug-in; prefer $$\xi/(\xi+1)$$ with a tracked $$\xi$$.
- Freezing $$P_N$$ forever after the first second of a call.
- No gain floor → abrupt zeros → musical noise return.
- Applying Wiener after a nonlinear AGC without accounting for changed noise PSD.
- Confusing **echo** (correlated with far-end reference) with **noise** (no reference)—Wiener NS is not AEC.

## Mini-lab

**Goal.** Evaluate Wiener gains at a priori SNRs of \(-10\), \(0\), and \(+10\,\mathrm{dB}\).

```python
import numpy as np

for snr_db in (-10, 0, 10):
    xi = 10 ** (snr_db / 10.0)
    G = xi / (xi + 1.0)
    print(snr_db, "xi", round(float(xi), 4), "G", round(float(G), 3),
          "G_dB", round(float(20 * np.log10(G)), 2))
```

**Expected.** \(-10\,\mathrm{dB}\) → \(\xi=0.1\), \(G\approx 0.091\) (\(-20.83\,\mathrm{dB}\)). \(0\,\mathrm{dB}\) → \(\xi=1\), \(G=0.5\) (\(-6.02\,\mathrm{dB}\)). \(+10\,\mathrm{dB}\) → \(\xi=10\), \(G\approx 0.909\) (\(-0.83\,\mathrm{dB}\)). The middle row is the point marked on the figure.

**Failure modes.** Passing decibels straight into \(\xi/(\xi+1)\) (forgetting \(10^{\mathrm{SNR}/10}\)) makes the \(-10\,\mathrm{dB}\) gain larger than the \(+10\,\mathrm{dB}\) gain, which is the curve upside down. Using \(20\log_{10}\) to convert SNR to \(\xi\), or reporting \(10\log_{10} G\) instead of \(20\log_{10} G\), shifts the decibel column by about a factor of two. \(\gamma/(\gamma+1)\) is a different plug-in; this lab does not estimate \(\gamma\).

## Exercises

1. **Algebra.** Show that $$G^{\mathrm{W}}=\xi/(\xi+1)$$ equals $$1-1/(\xi+1)$$ and interpret $$1-G$$ as the noise-attenuation factor.
2. **Numerical.** For $$\xi\in\{0.1,1,10\}$$ compute $$G$$ in linear and dB. At what $$\xi$$ is the gain $$-6\,\mathrm{dB}$$?
3. **Implement.** Code decision-directed Wiener on a WAV file; plot $$G(k,\ell)$$ as a spectrogram-like image; compare musical noise against spectral subtraction from 03-01.
4. **Concept link.** In two paragraphs, explain why a neural IRM estimator can beat a decision-directed Wiener on non-stationary noise *without* abandoning the $$\xi/(\xi+1)$$ intuition.

### Answer hints

1. Subtract the two forms; \(1-G=1/(\xi+1)\) is the fraction of \(Y\) you attribute to noise.
2. \(G(-6\,\mathrm{dB})=1/2\) when \(\xi=1\). The three requested gains are about \(0.091\), \(0.5\), and \(0.909\).
3. Plot \(G\), not \(|Y|\). A twitchy \(\eta\) looks speckled; spectral subtraction looks like holes.
4. The network is still aiming at a ratio of powers. It wins by estimating that ratio from more context than one decision-directed recursion, not by inventing a different gain shape.

## Further reading

- N. Wiener, *Extrapolation, Interpolation, and Smoothing of Stationary Time Series* (classical foundation).
- Y. Ephraim & D. Malah, “Speech enhancement using a minimum mean-square error short-time spectral amplitude estimator,” *IEEE TASSP*, 1984 (decision-directed SNR).
- P. Scalart and J. V. Filho, “Speech enhancement based on a priori signal to noise estimation,” *ICASSP*, 1996 — the a priori SNR form used in speech Wiener filters.
- P. C. Loizou, *Speech Enhancement: Theory and Practice* — textbook derivations of Wiener / MMSE estimators.
- SpeexDSP / WebRTC Audio Processing Module noise-suppression overview (engineering instantiations).
