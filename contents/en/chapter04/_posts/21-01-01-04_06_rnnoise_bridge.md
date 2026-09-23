---
layout: post
title: "04-06 RNNoise as a teaching bridge"
chapter: "04"
order: 6
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

**RNNoise** (Jean-Marc Valin, arXiv:1709.08243; [xiph/rnnoise](https://github.com/xiph/rnnoise)) is a Bark-band front-end, a pitch comb, and a small GRU that emits 22 gains. It does not match the DeepFilterNet3 Voicebank+Demand row (PESQ 3.17 in arXiv:2305.08227). It teaches the same shape — coarse bands plus a harmonic stage — with numbers you can check by hand.

![DeepFilterNet ERB path, used here as the contrast to RNNoise’s 22 Bark bands and GRU gains]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. DeepFilterNet’s picture: 32 ERB gains, then a 5-tap complex filter on the low STFT bins. RNNoise is the contrast, not a redraw of this figure: 22 Bark-scale bands, a GRU that predicts those band gains, and a pitch comb between harmonics. Both are hybrid. The bands, the second stage, and the net size differ.*

## Learning objectives

You will compute RNNoise’s band gain from the ideal ratio mask, list the 42 features and the 215-unit GRU stack from the paper, contrast that pipeline with DeepFilterNet’s 32 ERB bands and 5 complex taps, and name the systems lessons (frame API, smoothing, cache-sized weights) that transfer to an AudioWorklet even when the product ships DF3.

## 60-minute teaching plan

- **0–10 min** — Listen to the contrast: band gains versus a complex multi-tap filter.
- **10–25 min** — 22 bands, the gain formula, the pitch comb.
- **25–40 min** — 42 features, GRU, loss exponent $$\gamma=1/2$$, complexity.
- **40–50 min** — What to copy into a WASM port, and what not to expect on PESQ.
- **50–60 min** — Mini-lab, exercises.

## Core explanation

### Frame and bands

RNNoise runs at 48 kHz on **20 ms** windows with **50% overlap** (hop 10 ms, 480 samples), the same framing DeepFilterNet uses. Analysis and synthesis use the Vorbis window

$$
w(n)=\sin\left(\frac{\pi}{2}\sin^{2}\left(\frac{\pi n}{N}\right)\right),
$$

which satisfies the Princen–Bradley criterion, so constant-overlap-add of this window reconstructs a constant input. The spectrum is grouped into **22 bands**: the Opus codec’s Bark approximation (Bark spacing at high frequency, and at least four DFT bins per band at low frequency), with triangular weights $$w_b(k)$$ that sum to 1 across bands. Band energy is

$$
E(b)=\sum_k w_b(k)\,|X(k)|^{2}.
$$

The network does not emit 481 bin masks. It emits one gain per band. The training target is the square root of the ideal ratio mask,

$$
g_b=\sqrt{\frac{E_s(b)}{E_x(b)}},
$$

applied to bins by interpolating with the same triangles, $$r(k)=\sum_b w_b(k)\,\hat{g}_b$$. Gains live in $$[0,1]$$. That bound is the reason a tiny net is stable: a mapping network that predicts raw magnitudes has no such box.

DeepFilterNet’s envelope stage is the descendant of this idea with a different scale: **32 ERB bands** and a real gain, not 22 Bark bands. The second stage is the break. RNNoise does not predict complex STFT taps. It runs a **pitch comb**. If $$P(k)$$ is the DFT of the signal delayed by the pitch period $$T$$, the filter forms $$X(k)+\alpha_b P(k)$$ and renormalizes each band’s energy. The coefficient is a heuristic of the pitch correlation $$p_b$$ and the gain,

$$
\alpha_b=\min\left(\sqrt{\frac{p_b^{2}(1-g_b^{2})}{(1-p_b^{2})g_b^{2}}},\,1\right),
$$

with the boundary rules $$\alpha_b=1$$ when $$p_b\ge g_b$$, and $$\alpha_b=0$$ when $$g_b=1$$ or $$p_b=0$$. DeepFilterNet’s 5-tap complex sum can build a similar harmonic reinforcement inside the net, at a much higher MAC cost, and only up to about 5 kHz. RNNoise’s comb is DSP, cheap, and only as good as the pitch estimate.

### Features and the GRU

The 42 inputs are fixed by the paper: 22 Bark cepstral coefficients, first and second derivatives of the first 6 (12 more), 6 DCT coefficients of the pitch correlation, the pitch period, and one non-stationarity feature. $$22+12+6+1+1=42.$$ There is no cepstral mean normalization, so absolute level is visible. Mic response is trained in with a random second-order filter whose coefficients lie in $$[-3/8,3/8]$$.

The net has **215 units** and **four hidden layers**, the largest with 96 units. Valin reports that a GRU slightly beats an LSTM here and is simpler. A voice-activity output adds 24 weights and gives one GRU a speech-versus-noise job during training. The gain loss is

$$
L(g_b,\hat{g}_b)=\left(g_b^{\gamma}-\hat{g}_b^{\gamma}\right)^{2},\qquad \gamma=\tfrac{1}{2},
$$

not binary cross-entropy. $$\gamma\to 0$$ would approach a log-energy error and over-suppress; $$\gamma=1/2$$ is the paper’s operating point. Bands with no speech and no noise are marked undefined and dropped from the loss, which is how silence and low-passed audio avoid teaching the net to output 0.

Gain smoothing limits how fast a band may decay,

$$
\tilde{g}_b=\max\left(\lambda \tilde{g}_b^{(\mathrm{prev})},\,\hat{g}_b\right),\qquad \lambda=0.6,
$$

and the paper equates $$\lambda=0.6$$ at a 10 ms hop with a reverberation time of about **135 ms**. A smaller $$\lambda$$ sounds dry; $$\lambda=1$$ never releases. This one-pole floor is the anti-musical-noise trick Chapter 03 obtained from a spectral floor.

### Complexity you can put next to DeepFilterNet

The net has **87,503** weights. At 8 bits they fit an L2 cache; the paper reports no quality loss from that quantization. A multiply-add counted as two flops is about 175,000 flops per frame, **17.5 Mflop/s** at 100 frames per second. FFTs add about 7.5 Mflop/s and the 12 kHz pitch search about 10, near **40 Mflop/s** total. The non-vectorized C code used about **1.3%** of one Haswell i7-4800MQ core and about **14%** of a 1.2 GHz Cortex-A53. DeepFilterNet’s published budget is ~0.35 GMAC/s, far above 40 Mflop/s. In the DF2 table, RNNoise is PESQ **2.33**, RTF **0.027**, against simplified DF2 at PESQ **3.08**, RTF **0.04**: similar laptop RTF, lower PESQ on that set.

Training data is about 6 hours of speech and 4 hours of noise, expanded to 140 hours, resampled between 40 and 54 kHz. The ICASSP DeepFilterNet setup uses more than 750 hours of speech. A click or a language outside those 6 hours is a fair miss.

### What transfers to the product path

The product path is still the DF3-oriented AudioWorklet (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`), not an RNNoise port. Copy the habits: one hop per call (480 samples; a 128-sample quantum still needs the ring in 05-03); precompute the window and the band weights; smooth gains ($$\lambda=0.6$$ is RNNoise’s constant, not an untested DF3 default); quantize so weights stay in cache; keep the pitch comb if the net is this small. A GRU without the comb is a different algorithm.

## Pitfalls

- Dismissing the C code because PESQ is 2.33 on someone else’s table.
- Expecting the default RNNoise model to match PESQ 3.17.
- Porting the GRU and deleting the pitch filter.
- Using only RNNoise as the baseline for a 48 kHz DF3 regression. Keep it as a floor (“we still beat this”), not as the target.

## Mini-lab

**Goal.** Check the feature count, the flop budget, and one smoothed-gain step with the paper’s constants. No audio file and no network.

```bash
python3 - << 'PY'
bfcc, deriv, pitch_dct, pitch_period, nonstat = 22, 12, 6, 1, 1
features = bfcc + deriv + pitch_dct + pitch_period + nonstat
weights = 87503
flops_per_frame = weights * 2  # multiply-add counted as two flops
mflops = flops_per_frame * 100 / 1e6  # 10 ms hop
g_hat, g_prev, lam = 0.3, 0.9, 0.6
g_smooth = max(lam * g_prev, g_hat)
print(features, flops_per_frame, round(mflops, 1), round(g_smooth, 2))
PY
```

**Expected**. `42 175006 17.5 0.54`. The smoothed gain stays at $$0.6\times 0.9=0.54$$ because the new estimate 0.3 would have dropped the band too fast. The paper’s “175,000” is the same quantity rounded ($$2\times 87503=175006$$).

**Failure modes**. Forgetting the derivatives and reporting 22 features. Using a 20 ms hop and getting 8.8 Mflop/s. Setting $$\lambda=0$$ and calling the result “smoothed.” Cloning RNNoise into the product and claiming DF3 parity.

## Exercises

1. **Chain.** Draw PCM → 960-point window → 22 bands → 42 features → GRU → 22 gains → pitch comb → synthesis. Mark the 10 ms hop.
2. **Alpha.** $$g_b=1$$. What is $$\alpha_b$$, and what does the comb do to a clean frame?
3. **Smoothing.** Previous smoothed gain 0.8, new estimate 0.2, $$\lambda=0.6$$. What is the output gain? How many hops of a sustained 0.2 estimate does it take to fall under 0.3?
4. **API.** Sketch `process_frame(state, in[480], out[480])` and list three fields inside `state` that must survive the call.

### Answer hints

1. Hop 480 samples at 48 kHz. The GRU sees 42 inputs and emits 22 gains plus a VAD. The comb uses pitch period $$T$$ and per-band $$\alpha_b$$, then band energies are renormalized.
2. The formula is guarded: when $$g_b=1$$, $$\alpha_b=0$$. The comb is bypassed so clean speech is not pitch-filtered.
3. $$\max(0.6\times 0.8,\,0.2)=\max(0.48,\,0.2)=0.48$$. Next hop $$\max(0.6\times 0.48,\,0.2)=0.288$$, which is under 0.3. Two hops.
4. At least: GRU hidden state, the previous smoothed gains $$\tilde{g}_b$$, and the OLA / pitch history. Zeroing any of them mid-stream clicks or opens a short noise burst (lesson 05-04).

## Further reading

- Valin, “A Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement,” [arXiv:1709.08243](https://arxiv.org/abs/1709.08243). Published as the 2018 IEEE MMSP paper cited by DeepFilterNet.
- Source and the 8-bit weights: [github.com/xiph/rnnoise](https://github.com/xiph/rnnoise).
- SpeexDSP’s MMSE suppressor, the classical baseline in that paper.
- Schröter et al., [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) and [arXiv:2205.05474](https://arxiv.org/abs/2205.05474), for the 32-band ERB contrast and the PESQ 2.33 versus 3.08 table.
