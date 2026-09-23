---
layout: post
title: "03-03 Kalman-style tracking (intuition)"
chapter: "03"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter03
lesson_type: required
draft: false
---

Kalman filtering is not “another mask.” It is a **recursive Bayesian tracker**: predict the next speech state, then correct that prediction with a new noisy observation. In speech enhancement and acoustic echo control, Kalman-style thinking appears in adaptive filters, residual-echo trackers, and hybrid AEC+NS pipelines (for example classical Kalman AEC followed by a tiny neural postfilter). This lesson stays at the **intuition and block-diagram** level—enough to read papers and debug hybrids—without turning into a control-theory course.

## Learning objectives

You will explain the predict–update loop with process and measurement noise covariances, map speech enhancement to a state-space sketch, contrast Kalman tracking with per-frame Wiener gains, and identify product patterns where Kalman (or RLS/LMS adaptive filters) front-end a neural residual suppressor.

## 60-minute teaching plan

- **0–10 min** — Why recursive tracking beats “estimate from scratch every frame.”
- **10–25 min** — State-space model, predict step, Kalman gain intuition (no giant matrix slog).
- **25–40 min** — Speech/AEC instantiations: tracking AR speech coefficients or echo path.
- **40–50 min** — Hybrid story: Align-ULCNet-style Kalman AEC + neural postfilter (survey pointer).
- **50–60 min** — Pitfalls, exercises, link forward to WebRTC APM (03-04).

## Core explanation

### The one-sentence Kalman idea

Maintain a belief about a hidden state $$x_\ell$$ (for example, clean speech samples, LPC coefficients, or an echo-path impulse response). Each frame:

1. **Predict** using dynamics: $$x_{\ell|\ell-1} = A x_{\ell-1|\ell-1}$$ (plus process noise uncertainty).
2. **Update** with measurement $$y_\ell = H x_\ell + v_\ell$$: pull the prediction toward the observation in proportion to how trustworthy each is.

The **Kalman gain** $$K_\ell$$ is large when the measurement is reliable relative to the prediction—so you trust the mic more—and small when measurements are noisy—so you coast on the model.

### Tiny scalar cartoon

Suppose a scalar state with

$$
x_\ell = x_{\ell-1} + w_\ell, \qquad y_\ell = x_\ell + v_\ell,
$$

variances $$q=\mathrm{Var}(w)$$, $$r=\mathrm{Var}(v)$$. After predicting variance $$p^{-}=p+q$$, the gain is

$$
K = \frac{p^{-}}{p^{-} + r}, \qquad \hat{x} = \hat{x}^{-} + K\bigl(y - \hat{x}^{-}\bigr).
$$

Compare to Wiener: $$K$$ looks like $$\xi/(\xi+1)$$ if you read $$p^{-}/r$$ as a prior SNR. Kalman is Wiener **plus memory** through the predicted state and variance. In the figure, the orange noise floor is the kind of level a recursive tracker maintains, and the blue curve is the gain that floor would feed. A Kalman step is one statistically explicit way to update that floor; the picture itself is still classical NS, not a block diagram of the filter.

![A tracked noise floor beside the SNR gain that floor is used to compute]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Figure. The orange trace is a noise-floor tracker; the curve on the right is the gain that tracker feeds, which is the piece a Kalman update is trying to stabilize.*

### Why speech engineers care

| Use case | State $$x$$ | Measurement $$y$$ |
|----------|-------------|-------------------|
| Clean-speech tracker | speech samples / spectral amplitudes | noisy mic |
| LPC / formant tracker | AR coefficients | residual / short-time spectrum |
| AEC path estimate | echo impulse response $$\mathbf{h}$$ | mic, with far-end reference as regressor |
| Residual echo PSD | residual echo power | error after adaptive filter |

**Adaptive filters** (NLMS, RLS) used in AEC are close cousins: they recursively estimate an echo path. Kalman provides a statistically motivated gain schedule; NLMS provides a cheap normalized step-size heuristic. WebRTC APM and SpeexDSP historically lean on practical adaptive filters; research hybrids often say “Kalman AEC” when they mean a recursive echo-path tracker with covariance-aware steps.

### Hybrid classical + neural (product pattern)

A pattern that keeps reappearing in low-complexity AENR (acoustic echo and noise reduction):

1. Classical adaptive filter / Kalman cancels the **linear** echo given a far-end reference.
2. A **small neural** network (ULCNet-class, GTCRN-class, or DeepFilterNet postfilter) removes residual echo + noise that the linear model cannot catch (nonlinear loudspeaker distortion, non-stationary noise).

Survey pointers (name-level only, Chapter 04 will expand SE models): Align-ULCNet and related ULCNet+adaptive-filter hybrids; drone / GSC+DeepFilterNet2 pipelines where a spatial front-end feeds a neural enhancer.

**Engineering moral:** do not ask the neural net to learn pure linear echo cancellation from scratch if you already have a reference signal—give it a cleaned residual.

### Relation to Wiener (03-02)

- Wiener (typical STFT form): **stateless per frame** given $$\xi_\ell$$ (though $$\xi$$ itself may be recursive).
- Kalman: **stateful**; the gain depends on predicted covariance, not only on an SNR number.
- Decision-directed SNR tracking is a *poor man’s* recursive prior—conceptually between naive Wiener and full Kalman.

## Checklist: when to reach for Kalman-style thinking

- You have a **dynamics model** (echo path slowly varying; speech AR envelope).
- You have a **reference** (far-end audio for AEC).
- Residuals after a linear canceller still need a nonlinear cleaner.
- You must run **always-on** with bounded CPU—prefer classical adaptive filter + tiny NS over a huge end-to-end network.

## Pitfalls

- Treating Kalman as magic noise reduction without specifying state and measurement models.
- Underestimating model mismatch: wrong $$A$$ or $$H$$ → biased tracking.
- Letting covariance inflate numerically (need Joseph form / SPD fixes in real code).
- Using a full Kalman on huge STFT state vectors when a diagonal / per-bin approximation (or NLMS) is the practical choice.
- Forgetting that neural residual suppressors can **re-add latency** and streaming state (Chapters 05–06).

## Mini-lab

**Goal.** One scalar predict–update step. Print the Kalman gain for a trustworthy measurement and for a noisy one.

```python
def kalman_gain(p, q, r):
    p_pred = p + q
    return p_pred / (p_pred + r)

for r in (0.1, 10.0):
    K = kalman_gain(p=1.0, q=0.1, r=r)
    print("r", r, "K", round(K, 3))
```

**Expected.** Prior variance after the predict step is \(1.1\). For \(r=0.1\), \(K\approx 0.917\) (trust the measurement). For \(r=10\), \(K\approx 0.099\) (coast on the prediction). Same shape as a Wiener gain: large when the “SNR” \(p^{-}/r\) is large.

**Failure modes.** Updating \(p\) with the measurement before computing \(K\) changes both numbers. Swapping \(q\) and \(r\) makes the noisy sensor look more trustworthy than the clean one. This is a scalar cartoon of the gain, not a speech Kalman filter and not a noise-PSD tracker implementation.

## Exercises

1. **Scalar Kalman.** Implement the scalar predict–update equations in a notebook; drive $$x$$ with a slow sine and observe $$K$$ as you change $$r$$.
2. **Mapping.** Write a one-page diagram mapping AEC to state $$=\mathbf{h}$$, regressors $$=$$ far-end taps, measurement $$=$$ mic. Mark where a neural postfilter sits.
3. **Compare.** List three similarities and three differences between decision-directed Wiener and Kalman tracking for speech PSD.
4. **Design brief.** For a browser call with loudspeaker echo, propose a hybrid: WebRTC AEC → residual neural NS. State what each block is responsible for.

### Answer hints

1. \(K\) should fall as \(r\) rises, and the estimate should lag a fast wiggle in \(y\) when \(r\) is large.
2. Far-end taps are the regressor; the mic is \(y\); the neural block sees \(e=y-\hat{h}*x\), not the raw mic.
3. Both are recursive and both shrink the gain when noise dominates. Wiener (decision-directed) tracks a power ratio; Kalman tracks a state and a variance, and it has an explicit process model.
4. AEC owns linear echo given the far-end reference. The neural stage owns whatever is left: residual echo and ambient noise. Do not ask the network to rediscover \(\mathbf{h}\).

## Further reading

- R. E. Kalman, “A new approach to linear filtering and prediction problems,” *ASME J. Basic Eng.*, 1960 (foundational).
- Adaptive filter chapters in Haykin, *Adaptive Filter Theory* (NLMS/RLS as practical AEC engines).
- WebRTC Audio Processing Module overview (engineering AEC+NS chain).
- Survey pointers on hybrid Kalman/ULCNet AENR (Align-ULCNet and related ULCNet hybrid papers—name-level).
