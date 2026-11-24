---
layout: post
title: "10-01 Curated reading list"
chapter: "10"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter10
lesson_type: required
draft: false
---

Read three primary sources carefully rather than bookmarking twenty abstracts. Every link below is a real paper, repository, or doc set used in this course. Survey names at the bottom are names only: DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN. Do not invent their titles or URLs. If a reading card needs a fact you have not opened, write “not read” instead of a plausible sentence.

![DeepFilterNet ERB path and deep filter]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. The picture you should be able to redraw after reading Schröter et al.: STFT in, ERB gains and a deep filter, ISTFT and overlap-add out. The card template below is how you prove you read it.*

The speech-enhancement and audio-ML literature publishes hundreds of papers every year at ICASSP, INTERSPEECH, and NeurIPS—and trying to read them chronologically or randomly is a fast track to burnout. The secret to reading audio research like a senior engineer is **triangulation**: anchor yourself on a small canon of landmark papers that each unlocked a genuinely new architectural paradigm (classical Wiener/MMSE $$	o$$ RNNoise hybrid $$	o$$ Conv-TasNet time-domain $$	o$$ DeepFilterNet complex deep filtering $$	o$$ modern neural codecs and generative diffusion).

This curated reading map organizes the essential papers, textbooks, and open-source repositories by *what exact engineering bottleneck each one solved*.

---

## Background Knowledge Map: Five Paradigms Across the Speech-Enhancement Canon

Every paper on the reading list sits cleanly inside one of five intellectual lineages:

1. **Classical Statistical DSP (Ephraim–Malah, Boll, Loizou):** Wiener filtering, spectral subtraction, and MMSE-STSA—teaching you noise-floor tracking, musical noise, and why phase matters.
2. **Psychoacoustic Hybrids (RNNoise, PercepNet, DeepFilterNet):** Combining ERB/Bark critical bands and pitch/deep filtering with tiny GRUs to achieve sub-millisecond CPU inference at 48 kHz.
3. **End-to-End Time-Domain Separation (Conv-TasNet, Demucs):** Replacing fixed STFTs with learned filterbanks and dilated TCNs/U-Nets—great for source separation, revealing the latency-vs-compute trade-offs of raw waveforms.
4. **Perceptual Evaluation & Challenges (DNS Challenge, DNSMOS, SI-SDR / Le Roux et al.):** Defining how the field measures progress honestly without metric gaming.
5. **Generative Speech Restoration (Score/Diffusion & Flow Matching, Neural Audio Codecs):** Moving beyond masking (which cannot regenerate destroyed harmonics) to synthesizing clean speech from severely degraded inputs.

---

## What you should be able to do

You should be able to pick three links from the list, fill a four-bullet card for each, and match one filled example closely enough that a grader can see the shape. You should also keep SI-SDR, DNSMOS, RTF, and TrackProcessor as the English terms in your notes even when you write the surrounding prose in Vietnamese.

## Links you may cite

DeepFilterNet family:

- Schröter, Escalante-B., Rosenkranz, Maier. “DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio based on Deep Filtering.” ICASSP 2022. <https://arxiv.org/abs/2110.05588>
- Schröter et al. “DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio.” <https://arxiv.org/abs/2205.05474> (the later Interspeech 2023 write-up cites this paper as IWAENC 2022).
- Schröter, Escalante-B., Rosenkranz, Maier. “DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement.” Interspeech 2023. <https://arxiv.org/abs/2305.08227> — this is the DeepFilterNet3 model citation used by the upstream README. The results table in that paper names DeepFilterNet3; the paper title itself does not add a “3.”
- Code and model archive instructions: <https://github.com/Rikorose/DeepFilterNet>

Teaching bridges and runtimes:

- RNNoise: <https://github.com/xiph/rnnoise> and Valin, “A Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement,” <https://arxiv.org/abs/1709.08243>
- WebRTC APM: <https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/>
- SpeexDSP: <https://github.com/xiph/speexdsp>
- ONNX Runtime docs: <https://onnxruntime.ai/docs/>
- tract: <https://github.com/sonos/tract>

Evaluation and product:

- Le Roux, Wisdom, Erdogan, Hershey. “SDR – Half-baked or Well Done?” ICASSP 2019. Use it for SI-SDR, not as a listening test.
- DNS Challenge data and baselines: <https://github.com/microsoft/DNS-Challenge>
- DNSMOS / DNSMOS P.835: Reddy, Gopal, Cutler, Interspeech 2021 and ICASSP 2022. Non-intrusive. No official score threshold lives in this course.
- LiveKit docs: <https://docs.livekit.io/>
- npm `deepfilternet3-noise-filter` 1.3.0: <https://www.npmjs.com/package/deepfilternet3-noise-filter>
- Product repo (read, do not submit course patches here): <https://github.com/mezonai/mezon-noise-suppression>

## Card template

Four bullets, no more. This is the shape the mini-lab expects.

```text
Source: <url>
- Claim: one sentence from the abstract or README, not a guess.
- Streaming / latency: causal or not, hop or look-ahead if the source states it, else "not stated".
- What it measures or ships: metrics, a library, or an API. Use SI-SDR, DNSMOS, RTF, TrackProcessor only when the source actually discusses them.
- What I will reuse: one action in your harness or capstone.
```

Filled example (do not submit this URL as one of your three unless you also write two others):

```text
Source: https://arxiv.org/abs/2110.05588
- Claim: DeepFilterNet enhances full-band speech with an ERB gain stage plus deep filtering, at low complexity.
- Streaming / latency: The framework targets real-time full-band enhancement; check the paper for the stated window, hop, and any look-ahead before you quote a millisecond figure.
- What it measures or ships: The paper reports intrusive enhancement metrics on its test sets and describes the two-stage filter. It is not a LiveKit TrackProcessor.
- What I will reuse: I will redraw the ERB-plus-deep-filter block in my capstone sketch and I will not describe the npm wrapper as the algorithm.
```

The example refuses a fake latency number. That refusal is part of the shape. If you open the PDF and find the hop, you may replace “check the paper” with the figure you read, and you should say you read it.

## How to read one of these in an hour

Start with the figure, not the related-work section. For a DeepFilterNet paper, find the ERB path and the deep-filter sum. For DNSMOS, confirm it is non-intrusive and write down the listening protocol it was trained to track. For the npm README, copy the public names only: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setProcessor`, `setSuppressionLevel`, `setEnabled`, `assetConfig.cdnUrl`, and the `v2/` prefix behavior on ≥ 1.2.0. For WebRTC APM or SpeexDSP, note that they are classical baselines, not drop-in weights for the Mezon CDN.

Survey names, listed so you can recognize them in a talk and then stop: DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN. A card that invents an arXiv id for one of these fails the assignment.

## Mini-lab

Choose **three** URLs from the list above. Write `reading_cards.md` with three cards in the four-bullet shape. Then run:

```python
from pathlib import Path
text = Path("reading_cards.md").read_text()
sources = text.count("Source:")
bullets = text.count("\n- ")
print("sources", sources)
print("bullets", bullets)
print("has_url", "https://" in text)
```

Expected output:

```text
sources 3
bullets 12
has_url True
```

Twelve bullets is three cards times four bullets. Failure modes: a card whose claim contradicts the title you did not open; a fabricated URL for GTCRN or DeepFilterGAN; using the filled example as all three cards; translating SI-SDR or DNSMOS into a different acronym.

---

### Worked Numerical Example: Comparing Four Landmark Architectures Side by Side

Use this concrete scale table to orient yourself whenever you open a new speech-enhancement paper:

| Landmark Architecture | Domain / Front-End | Approx. Params | Typical Latency | Core Engineering Breakthrough |
| :--- | :--- | :--- | :--- | :--- |
| **RNNoise (2017)** | 22 Bark bands + pitch | $$\sim 88	ext{ K}$$ | $$20	ext{ ms}$$ | Ultra-tiny hybrid DSP + GRU in pure C |
| **DeepFilterNet (2022–23)** | 32 ERB + 96 complex DF bins | $$\sim 1.8	ext{ M}$$ | $$20	ext{–}40	ext{ ms}$$ | Two-stage ERB gain + complex deep filtering |
| **Conv-TasNet (2019)** | Learned 1D encoder (raw wave) | $$\sim 5.1	ext{ M}$$ | $$2	ext{ ms}$$ (causal) | End-to-end time-domain TCN separation |
| **DNS-Demucs (2020)** | Waveform U-Net + LSTM | $$\sim 18	ext{ M}$$ | $$40	ext{ ms}$$ | High-capacity real-time waveform denoising |

Look at the ratio across the table: **DeepFilterNet** uses **20× more parameters than RNNoise** to add complex harmonic restoration, yet still stays **10× smaller than Demucs**—illustrating the exact Pareto frontier between model size, latency, and perceptual quality!

### Deep-Dive Explanation: How to Read an Audio Paper in 20 Minutes Without Getting Lost (Read Slowly)

1. **Check four numbers on Page 1–3 before reading a single equation:** Sample rate (16 kHz vs 48 kHz), causal vs. non-causal (algorithmic latency!), MACs/s or RTF on CPU, and parameter count.
2. **Always listen to the authors’ audio demo page:** A paper with +0.8 dB higher SI-SDR can still sound metallic or over-smoothed on real speech; 30 seconds of listening tells you more than three tables.
3. **Spot the *delta* from its predecessor:** Ask *"what single bottleneck did the previous paper hit, and what exact mechanism here fixes it?"* (e.g., RNNoise’s real band gains $$	o$$ DeepFilterNet’s complex deep filter).
4. **Reproduce one tiny piece in code:** Even implementing just the paper’s STFT framing or loss function in 40 lines of Python/Rust cements the idea permanently.

**Quick check.** When comparing two speech-enhancement papers, why is it misleading to compare Paper A’s **16 kHz non-causal** SI-SDR directly against Paper B’s **48 kHz causal (20 ms latency)** SI-SDR?

---

## Exercises

1. Produce the three cards. Include at least one DeepFilterNet URL and one non-paper URL (repo or docs).
2. After you actually open arXiv:2110.05588, add a fifth private note (not part of the four bullets) with the hop or look-ahead you found, or “I did not find it.”
3. Open the DNS Challenge repo long enough to name one directory or script that is really there. Put that name in the “ships” bullet.
4. Write one sentence on why DNSMOS has no official cutoff in your card.
5. List the survey names you will **not** cite with a URL.

### Answer hints

1. Paper plus repo is the minimum mix. The npm page and LiveKit docs count as non-papers.
2. Keep the four-bullet contract intact. Extra notes go underneath.
3. Do not describe a file you have not seen. “not stated” is allowed.
4. Reddy, Gopal, and Cutler give a predictor, not a Mezon ship line. Domain shift is the failure mode.
5. DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, English. **xem trước.** Watch this beside the DeepFilterNet paper on the reading list. The talk follows the paper's block diagram; it does not replace the PDF.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, English. The DNS Challenge and DNSMOS portions match the dataset and metric readings in the same list.
- [But what is the Fourier Transform?  A visual introduction.](https://www.youtube.com/watch?v=spUNpyF58BY) — 3Blue1Brown, English. Use the visual transform as the intuition under the DSP readings, then return to the formulas.
