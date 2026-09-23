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

Neural speech enhancement (SE) replaces a hand-tuned gain with a model trained on noisy–clean mixtures. This lesson maps masking, mapping, and generative SE, waveform versus short-time Fourier transform (STFT) models, and the losses those models actually optimize, so DeepFilterNet (04-02 onward) and RNNoise (04-06) sit on a map you can defend. The architecture this course unpacks is the two-stage graph below.

![Two-stage DeepFilterNet graph: ERB envelope gains and a complex deep filter on the STFT]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. The graph this course unpacks: a coarse equivalent-rectangular-bandwidth (ERB) stage estimates a spectral envelope, then a short complex deep filter restores harmonics. Later lessons open each block; this lesson only fixes the map.*

## Learning objectives

You will contrast masking, mapping, and generative SE; separate the compressed spectral loss DeepFilterNet trains from the SI-SDR it only reports; and separate algorithmic latency from real-time factor (RTF).

## 60-minute teaching plan

- **0–10 min** — From the Wiener ideal ratio mask (IRM) to a learned mask: what paired data buys.
- **10–25 min** — Masking vs mapping vs generative; time domain vs STFT.
- **25–40 min** — DNS-style mixtures and the losses in the DeepFilterNet papers.
- **40–50 min** — Streaming constraints; 40 ms algorithmic delay is not an RTF.
- **50–60 min** — Mini-lab, pitfalls, exercises.

## Core explanation

### What the network outputs

**1. Masking.** Predict a mask $$M(k,\ell)$$ and form $$\hat{S}=M\odot Y$$. A real mask keeps the noisy phase. A complex ratio mask (CRM) multiplies real and imaginary parts and can rotate phase per bin, but it is still a single tap: one coefficient times one bin. The ideal ratio mask echoes the Wiener gain $$\xi/(\xi+1)$$ from Chapter 03. The ICASSP 2022 DeepFilterNet paper (arXiv:2110.05588) treats a CRM as the special case of deep filtering with filter order $$N=1$$ and look-ahead $$\ell=0$$.

**2. Mapping.** Predict clean magnitudes or the complex spectrum directly, $$\hat{S}=f_\theta(Y)$$. Nothing forces the output to stay near $$Y$$, so a weak loss over-smooths harmonics into a blurry envelope.

**3. Generative SE.** A GAN or diffusion model draws speech from a posterior. A second network still has to finish inside the hop. DeepFilterGAN (04-04) is a survey name only: no paper title or URL in this course.

### Time domain versus spectrogram models

| Family | Input | What you pay | What you get |
|--------|-------|--------------|--------------|
| Waveform (Conv-TasNet-like) | PCM frames | A learned encoder on every sample | Phase is implicit; full-band 48 kHz is expensive |
| STFT mask | Complex spectrogram | One window of latency | Interpretable gains; CRM cannot rebuild a harmonic the window smeared |
| ERB gain + deep filter | 32 ERB bands, then a few complex taps | Implementation of two stages | DeepFilterNet’s operating point |

At 48 kHz a 20 ms window (960 samples) has bin spacing $$48000/960=50$$ Hz. A pointwise mask cannot pull noise out from between harmonics finer than a bin, which is why stage 2 exists. These models are spectrogram systems for a full-band CPU budget.

### A DNS-style training mixture, with the numbers from the paper

The ICASSP 2022 framework trains on Deep Noise Suppression (DNS) challenge material: more than 750 hours of full-band clean speech and 180 hours of noise, VCTK and PTDB oversampled by 10, up to five noises at SNRs in $$\{-5,0,5,10,20,40\}$$ dB, random second-order filters, gains in $$\{-6,0,6\}$$ dB, and room impulse responses. Another 10,000 image-source RIRs are simulated at 48 kHz with RT60 from 0.05 s to 1.00 s. A café outside that RT60 range, or a noise those 180 hours never contained, was never supervised. DNSMOS (Chapter 08) scores the result; a leaderboard rank is not a product requirement.

### Loss families, and the one DeepFilterNet trains

Families you will see elsewhere: magnitude MSE, complex spectral error, time-domain SI-SDR, multi-resolution STFT, and adversarial critics. The ICASSP 2022 recipe does **not** train on SI-SDR. It uses a compressed spectral loss with exponent $$c=0.6$$,

$$
\mathcal{L}_{\mathrm{spec}}=\sum_{k,f}\left\||Y|^{c}-|S|^{c}\right\|^{2}+\sum_{k,f}\left\||Y|^{c}e^{j\varphi_Y}-|S|^{c}e^{j\varphi_S}\right\|^{2},
$$

plus a small auxiliary term (weight $$0.05$$) that pushes the deep-filter blend weight toward zero when the local SNR below the deep-filter cutoff is under $$-10$$ dB, and toward one when that SNR is above $$-5$$ dB. SI-SDR is an **evaluation** number in that paper: 16.63 dB for the full model on the VCTK/DEMAND test set, against 13.81 dB when stage 2 is removed. Wideband PESQ on the same table is 2.81 versus 2.57 without stage 2. Quote those only as that table’s numbers, on that set, for that checkpoint.

### Streaming is a different graph, not a smaller offline net

An offline Transformer may attend over the whole utterance. A VoIP hop cannot. The 2023 demo (arXiv:2305.08227) uses 20 ms windows, a 10 ms hop, and two frames of look-ahead: **40 ms of algorithmic latency**. That delay is not RTF.

$$
\mathrm{RTF}=\frac{T_{\mathrm{wall}}}{T_{\mathrm{audio}}}.
$$

A 10 ms hop that burns 4 ms of CPU has RTF 0.4 while the user still waits 40 ms. Causal convolutions and a fixed-size GRU (gated recurrent unit) replace a growing attention cache. Chapter 05 times the tail of $$T_{\mathrm{wall}}$$: a mean RTF of 0.4 with p95 above 1 still clicks.

### Where the named systems sit

```text
 low complexity                         higher quality on the published full-band tests
     │                                              │
  RNNoise ── ultra-light names (04-05) ── DeepFilterNet / 2 / 3 ── survey names (04-04)
  22 Bark bands + GRU                   32 ERB bands + 5-tap complex filter
```

RNNoise (Valin, arXiv:1709.08243) predicts 22 band gains with a small GRU and a pitch comb. DeepFilterNet predicts 32 ERB gains and five complex taps on the low bins. The npm package `deepfilternet3-noise-filter` runs a DF3-oriented ONNX/WASM graph in an AudioWorklet; it is not a bit-exact claim against the paper checkpoint, and it is not the RNNoise branch (04-06).

## Pitfalls

- Ranking an offline PESQ against a streaming RTF.
- Debugging a −15 dB subway clip as a model bug when the mix grid stopped at −5 dB.
- Reusing noisy phase and skipping the listening pass.
- Treating the npm wrapper as the algorithm. The algorithm is the STFT, the ERB gains, the taps, and the state across hops.

## Mini-lab

**Goal.** Compute algorithmic latency and RTF for the published 20 ms / 10 ms / two-frame look-ahead setup, and show they are different quantities.

```bash
python3 - << 'PY'
window_ms, hop_ms, lookahead_frames = 20.0, 10.0, 2
# Published overall delay for this configuration: window plus two hops.
algo_ms = window_ms + lookahead_frames * hop_ms
wall_ms = 4.0  # one hop of steady compute on a laptop you just timed
rtf = wall_ms / hop_ms
print(f"algorithmic_latency_ms={algo_ms:.1f}")
print(f"rtf={rtf:.2f}")
print("latency_is_rtf", algo_ms == wall_ms)
PY
```

**Expected**. `algorithmic_latency_ms=40.0`, `rtf=0.40`, `latency_is_rtf False`. The 40 ms figure is the delay stated for this window and look-ahead in the DeepFilterNet2 paper and in the 2023 demo write-up. The 4 ms wall time is a lab assumption, not a phone measurement.

**Failure modes**. Using hop as the latency (you report 10 ms and ignore the 20 ms window and the two future frames). Dividing wall time by the window instead of the hop (RTF looks half as large). Pasting a laptop RTF into a phone budget.

## Exercises

1. **Taxonomy.** Place RNNoise, a magnitude-IRM U-Net, Conv-TasNet, and DeepFilterNet into masking / mapping / generative and waveform / STFT. Say what each one multiplies or filters.
2. **Latency.** Window 20 ms, hop 10 ms, look-ahead 2 frames. State the algorithmic latency before any neural timing. What extra delay appears if the synthesis ring holds one extra hop?
3. **Loss.** The training loss uses $$c=0.6$$ on magnitudes and a phase-aware term. SI-SDR on the paper’s table is 16.63 dB. Which number would you monitor during training, and which only on a fixed test set?
4. **Data.** Give one user-audible failure for each of: SNRs only down to −5 dB, RT60 only up to 1 s, and noise drawn from 180 hours that lack keyboard clicks.

### Answer hints

1. RNNoise: real band gains (masking) on an STFT/Bark grid, plus a DSP pitch comb. IRM U-Net: masking, STFT. Conv-TasNet: learned waveform basis, closer to mapping. DeepFilterNet: real ERB mask plus a multi-tap complex filter on the STFT, not a generative model.
2. $$20+2\times 10=40$$ ms. One extra hop in the ring adds another 10 ms of buffering delay and does not change RTF.
3. Monitor $$\mathcal{L}_{\mathrm{spec}}$$ (and the auxiliary gate term) during training. Report SI-SDR only on the pinned test set; it is not the training objective in that paper.
4. −15 dB is outside the mix grid. A 1.5 s room was never in the 0.05–1.00 s RT60 set. Short clicks are unlike the long noises in those 180 hours.

## Further reading

- Schröter et al., ICASSP 2022, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588).
- Schröter et al., DeepFilterNet2, IWAENC 2022, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474).
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227); the README associates this citation with DeepFilterNet3. Code: [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Valin, [arXiv:1709.08243](https://arxiv.org/abs/1709.08243), [xiph/rnnoise](https://github.com/xiph/rnnoise). DNS Challenge overviews for the mixture protocol.
