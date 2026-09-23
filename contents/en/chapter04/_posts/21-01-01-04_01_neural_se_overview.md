---
layout: post
title: "04-01 Neural speech enhancement overview"
chapter: "04"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

Neural speech enhancement (SE) replaces hand-designed gains with a model trained on large noisy–clean mixtures. This overview lesson maps the design space—**masking vs mapping vs generative** SE, time-domain vs spectrogram models, loss families, and why **streaming** architectures differ from offline Transformers—so the DeepFilterNet family (04-02+) and RNNoise (04-06) have a clear place on the map. Citations stay with well-known landmarks: RNNoise, DNS Challenge, DeepFilterNet.

## Learning objectives

You will contrast mask estimation, spectral mapping, and generative SE; list common supervised losses at a high level; explain why causal / streaming graphs forbid naive bidirectional context; and place RNNoise and DeepFilterNet on a complexity–quality sketch for product work.

## 60-minute teaching plan

- **0–10 min** — From Wiener IRM to learned masks: what data buys you.
- **10–25 min** — Masking vs mapping vs generative; time vs STFT domain.
- **25–40 min** — Training mixtures (DNS-style), losses (magnitude, SI-SDR, complex, perceptual).
- **40–50 min** — Streaming constraints vs offline SE; RTF preview (Ch. 05).
- **50–60 min** — Pitfalls, exercises, reading map into 04-02.

## Core explanation

### What the network outputs

**1. Masking.** Predict a mask $$M(k,\ell)$$ and form $$\hat{S}=M\odot Y$$ (or apply to magnitude and reuse noisy phase). Ideal ratio mask targets echo the Wiener gain $$\xi/(\xi+1)$$ from Chapter 03. Variants: ideal binary mask (IBM), complex IRM, phase-sensitive masks.

**2. Mapping / regression.** Predict clean magnitudes or complex spectra directly $$\hat{S}=f_\theta(Y)$$. More flexible; easier to over-smooth speech if the loss is weak.

**3. Generative SE.** Score-based / GAN / diffusion-style models synthesize speech consistent with a posterior. Higher quality ceilings in offline settings; harder to stream at low RTF. DeepFilterGAN (survey, 04-04) attaches a lightweight GAN regenerator to a DeepFilterNet-style predictor.

### Time-domain vs spectrogram models

| Family | Input | Pros | Cons |
|--------|-------|------|------|
| Waveform (Conv-TasNet-like) | PCM frames | End-to-end phase | Heavy for full-band realtime |
| STFT mask / filter | Complex spectrogram | Interpretable, efficient | Window latency |
| Hybrid ERB + fine filter | Cochlear-like bands + STFT | DeepFilterNet sweet spot | Implementation complexity |

DeepFilterNet-class models are **spectrogram / deep-filtering** systems optimized for **full-band (48 kHz)** real-time CPU budgets—not raw waveform giants.

### Supervised training recipe (DNS-style)

1. Sample clean speech, noise, and optionally RIRs.
2. Mix at random SNRs (and reverb levels).
3. Train $$f_\theta$$ to recover clean speech or a mask.
4. Validate with intrusive metrics (SI-SDR, PESQ/STOI where licensed) and non-intrusive DNSMOS (Chapter 08).

The **Deep Noise Suppression (DNS) Challenge** series popularized large-scale training sets and baselines for real-time NS—read their overview papers for dataset and metric conventions, not as a claim that one network always wins.

### Loss families (high level)

- **Spectral MSE / MAE** on magnitude or log-magnitude — simple, may ignore phase.
- **Complex spectral losses** — penalize real/imag errors.
- **Time-domain SI-SDR** — scale-invariant signal improvement (Ch. 08).
- **Multi-resolution STFT losses** — stabilize perceptual quality.
- **Perceptual / discriminator losses** — GAN or PESQ-inspired critics (heavier).

Production streaming models often combine a complex / multi-resolution spectral term with a time-domain term; exact recipes belong to each paper (DeepFilterNet2/3, RNNoise).

### Why streaming ≠ offline Transformer SE

Offline models may use future frames (look-ahead) or full-sequence attention. Real-time VoIP constraints:

- **Algorithmic latency** ≈ window + look-ahead + buffering (Ch. 02, 05).
- **Causal convolutions / uni-directional RNNs** only.
- **Fixed state size** (GRU/LSTM hidden state)—no growing KV cache.
- **RTF ≪ 1** on target CPU (Ch. 05), often in WASM (Ch. 06).

A large bidirectional SE Transformer can win a leaderboard and still be unusable in AudioWorklet.

### Landmarks on the map

```text
 low complexity                    higher quality
     │                                    │
  RNNoise ────── ultra-light CRNs ────── DeepFilterNet2/3 ── generative refine
  (hybrid DSP+small net)   (GTCRN, μNet…)   (ERB+deep filter)   (DeepFilterGAN…)
```

Mezon’s `deepfilternet3-noise-filter` sits on the DF3-quality branch with on-device constraints—not on the RNNoise branch—but RNNoise remains the best **teaching bridge** (04-06).

## Pitfalls

- Comparing offline PESQ to streaming RTF unfairly.
- Training only on synthetic stationary noise then deploying in cafés.
- Ignoring phase / using magnitude-only masks at low SNR without listening tests.
- Assuming “larger Transformer” is always better for product NS.
- Treating the npm wrapper as the algorithm (Chapter 09 reminder).

## Exercises

1. **Taxonomy.** Classify RNNoise, a magnitude IRM U-Net, Conv-TasNet, and DeepFilterNet into masking/mapping/generative and time/STFT.
2. **Latency budget.** If hop = 10 ms and look-ahead = 2 frames, what algorithmic latency lower bound do you cite before neural compute?
3. **Loss choice.** Argue for SI-SDR vs log-mel MSE for a streaming telephony model.
4. **Reading.** Skim the DNS Challenge overview; list three dataset properties that affect product generalization.

## Further reading

- RNNoise paper and repository (Jean-Marc Valin et al.) — classic lightweight hybrid.
- Deep Noise Suppression Challenge overview papers / datasets (Microsoft DNS Challenge series).
- DeepFilterNet paper — full-band real-time SE baseline for this course.
- Loizou, *Speech Enhancement* — classical backdrop for mask targets.
