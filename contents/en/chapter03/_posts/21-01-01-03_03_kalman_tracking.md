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

Imagine tracking a speaker’s room echo path as someone walks across a conference room, or tracking a slowly drifting noise floor during a live call. Estimating from scratch on every single 10 ms frame wastes everything you already learned one frame ago; freezing the old estimate forever falls behind the room.

The **Kalman filter** solves that tension cleanly: it is not “just another spectral mask,” but a **recursive Bayesian tracker** that alternates between *predicting* where the hidden state moved and *updating* that belief with the latest microphone sample—weighted by how uncertain each side is. This lesson builds the Kalman intuition at the block-diagram level and shows why modern low-complexity audio products pair a classical Kalman/adaptive linear filter with a tiny neural residual cleaner.

![A tracked noise floor beside the SNR gain that floor is used to compute]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Figure. The orange trace is a noise-floor tracker; the curve on the right is the gain that tracker feeds, which is the piece a Kalman update is trying to stabilize.*

**Lesson roadmap:** Key ideas (state-space dynamics, Kalman gain as adaptive Wiener, hybrid classical + neural AENR) → Scalar predict–update model & speech/AEC state-space table → Worked example: tracing one concrete scalar predict–update step by hand for $$r = 0.1$$ vs. $$r = 10.0$$ → Explanation: 3 steps explaining why Kalman is “Wiener plus memory” → Checklist, Pitfalls, Mini-lab, Exercises & Videos.

---

## Key ideas: Recursive State-Space Estimation in Audio

### 1. State-Space Modeling — Separating Dynamics from Observation
A state-space model writes two equations: a **process equation** describing how the hidden state $$x_\ell$$ evolves over time (with process-noise variance $$q$$), and a **measurement equation** describing how the noisy microphone $$y_\ell$$ observes it (with measurement-noise variance $$r$$).

### 2. Kalman Gain $$K$$ = Dynamic Trust Knob
At every hop, the predicted variance grows to $$p^- = p + q$$, and the **Kalman gain** $$K = p^- / (p^- + r)$$ decides how much to trust the fresh microphone reading. Notice its exact algebraic twin: writing $$\xi = p^-/r$$ turns $$K$$ into $$\xi / (\xi + 1)$$—the Wiener gain from Lesson 03-02, now upgraded with evolving memory!

### 3. The Hybrid Classical + Neural Product Pattern
In acoustic echo and noise reduction (AENR), asking a neural network to learn a 200-tap linear room echo path from scratch is wasteful. Production hybrids (e.g., Kalman/NLMS AEC $$\to$$ ULCNet / DeepFilterNet postfilter) let a recursive linear tracker cancel the linear echo first, then hand the clean residual to a lightweight neural network.

---

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

1. **Predict** using dynamics: $$x_{\ell\vert\ell-1} = A x_{\ell-1\vert\ell-1}$$ (plus process noise uncertainty).
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

---

### Explanation: Tracing One Scalar Kalman Update Step by Hand

Suppose our previous state estimate is $$\hat{x}_{0} = 2.0$$ with uncertainty variance $$p = 1.0$$, process noise $$q = 0.1$$, and a fresh microphone measurement arrives at $$y_1 = 5.0$$:

#### Step 1: Predict (uncertainty grows)
Before seeing $$y_1$$, our prediction stays $$\hat{x}^- = 2.0$$, and its variance grows by the process noise:
$$
p^- = p + q = 1.0 + 0.1 = 1.1.
$$

#### Step 2: Compute the Kalman gain $$K$$ under clean vs. noisy sensors
- **Trustworthy sensor ($$r = 0.1$$):** $$K = \frac{1.1}{1.1 + 0.1} \approx 0.917$$ $$\implies \hat{x}_1 = 2.0 + 0.917(5.0 - 2.0) = 4.75$$ (jumps straight toward the fresh measurement!), and posterior variance collapses to $$p_1 = (1 - 0.917)(1.1) \approx 0.091$$.
- **Noisy sensor ($$r = 10.0$$):** $$K = \frac{1.1}{1.1 + 10.0} \approx 0.099$$ $$\implies \hat{x}_1 = 2.0 + 0.099(5.0 - 2.0) = 2.30$$ (barely budges—coasts safely on the prior!), and posterior variance stays near $$0.99$$.

#### Step 3: Why covariance-aware steps beat fixed step sizes in AEC
When the far-end talker is silent or double-talk erupts, the effective measurement noise $$r$$ spikes—automatically shrinking the Kalman gain $$K \to 0$$ and freezing the echo-path estimate without brittle manual switches!

Summary of the Kalman loop:

$$
(\hat{x}_{\ell-1}, p_{\ell-1})
\;\xrightarrow{\text{Predict } (+q)}\;
(\hat{x}^-, p^-)
\;\xrightarrow{K = \frac{p^-}{p^- + r}}\;
\hat{x}_\ell = \hat{x}^- + K(y_\ell - \hat{x}^-).
$$

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

**Expected.** Prior variance after the predict step is $$1.1$$. For $$r=0.1$$, $$K\approx 0.917$$ (trust the measurement). For $$r=10$$, $$K\approx 0.099$$ (coast on the prediction). Same shape as a Wiener gain: large when the “SNR” $$p^{-}/r$$ is large.

**Failure modes.** Updating $$p$$ with the measurement before computing $$K$$ changes both numbers. Swapping $$q$$ and $$r$$ makes the noisy sensor look more trustworthy than the clean one. This is a scalar cartoon of the gain, not a speech Kalman filter and not a noise-PSD tracker implementation.

## Exercises

1. **Scalar Kalman.** Implement the scalar predict–update equations in a notebook; drive $$x$$ with a slow sine and observe $$K$$ as you change $$r$$.
2. **Mapping.** Write a one-page diagram mapping AEC to state $$=\mathbf{h}$$, regressors $$=$$ far-end taps, measurement $$=$$ mic. Mark where a neural postfilter sits.
3. **Compare.** List three similarities and three differences between decision-directed Wiener and Kalman tracking for speech PSD.
4. **Design brief.** For a browser call with loudspeaker echo, propose a hybrid: WebRTC AEC → residual neural NS. State what each block is responsible for.

### Answer hints

1. $$K$$ should fall as $$r$$ rises, and the estimate should lag a fast wiggle in $$y$$ when $$r$$ is large.
2. Far-end taps are the regressor; the mic is $$y$$; the neural block sees $$e=y-\hat{h}*x$$, not the raw mic.
3. Both are recursive and both shrink the gain when noise dominates. Wiener (decision-directed) tracks a power ratio; Kalman tracks a state and a variance, and it has an explicit process model.
4. AEC owns linear echo given the far-end reference. The neural stage owns whatever is left: residual echo and ambient noise. Do not ask the network to rediscover $$\mathbf{h}$$.

## Further reading

- R. E. Kalman, “A new approach to linear filtering and prediction problems,” *ASME J. Basic Eng.*, 1960 (foundational).
- Adaptive filter chapters in Haykin, *Adaptive Filter Theory* (NLMS/RLS as practical AEC engines).
- WebRTC Audio Processing Module overview (engineering AEC+NS chain).
- Survey pointers on hybrid Kalman/ULCNet AENR (Align-ULCNet and related ULCNet hybrid papers—name-level).

## Video tham khảo

- [Why Use Kalman Filters? | Understanding Kalman Filters, Part 1](https://www.youtube.com/watch?v=mwn8xhgNpFY) — MATLAB, English. **xem trước.** Watch the predict-then-correct picture. A noise tracker that only updates a floor is the same two-step idea with a much smaller state.
- [Kalman Filter - VISUALLY EXPLAINED!](https://www.youtube.com/watch?v=-DiZGpAh7T4) — Kapil Sachdeva, English. The visual update is the part to watch: uncertainty shrinks when a measurement arrives, which is the intuition behind a recursive speech tracker.
