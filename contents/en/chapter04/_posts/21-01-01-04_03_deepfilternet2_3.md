---
layout: post
title: "04-03 DeepFilterNet2 and DeepFilterNet3"
chapter: "04"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

DeepFilterNet2 and DeepFilterNet3 keep the ERB-plus-deep-filter split and change the training loss, the amount of temporal buffering, a post-filter, and an SNR gate. This lesson only uses numbers printed in arXiv:2205.05474 and arXiv:2305.08227. It does not invent block names, and it does not claim the npm package matches those checkpoints bit for bit.

![Same ERB-plus-deep-filter skeleton across DeepFilterNet generations]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. The skeleton stays: 32 ERB gains for the envelope, then a 5-tap complex filter on the low bins. Across versions the published changes are the loss and the data (multi-resolution STFT, DNS4, a post-filter), fewer temporal buffers inside the net, and an SNR gate that can skip a stage. Module names you have not read in the paper are not part of this caption.*

## Learning objectives

You will state what DeepFilterNet2 changed relative to the ICASSP 2022 model (runtime buffers, multi-resolution loss, post-filter, reported RTF), what the Interspeech 2023 paper adds as a local-SNR gate and a DeepFilterNet3 row on Voicebank+Demand, and how `deepfilternet3-noise-filter` relates to that family without being a second source of truth for the weights.

## 60-minute teaching plan

- **0–10 min** — Recap: 32 ERB bands, 5 taps, 20 ms / 10 ms, 40 ms delay.
- **10–25 min** — DF2: where the 0.04 RTF comes from, and where it does not.
- **25–40 min** — The 2023 gate and the DF3 row on the metric table.
- **40–50 min** — RIR mismatch, ONNX export, the npm surface.
- **50–60 min** — Mini-lab, exercises.

## Core explanation

### Same DNA, different checkpoints

All three generations target 48 kHz, a 20 ms window, 50% overlap, 32 ERB bands, and a 5-tap filter up to about 5 kHz, with two frames of look-ahead quoted as **40 ms** of delay. Pin a weight file, not the word “DeepFilterNet.” A DF2 checkpoint in a DF3 config is a shape error or a timbre error.

### DeepFilterNet2 — arXiv:2205.05474

DeepFilterNet2, “Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio” (IWAENC 2022, arXiv:2205.05474), keeps that STFT. The changes that move quality and speed are:

- **Loss.** Warmup of 3 epochs, then cosine decay, updated every step. A multi-resolution spectral loss after the inverse STFT uses windows of 5, 10, 20, and 40 ms with compression $$c=0.3$$. The ICASSP $$\alpha$$ loss is dropped; a 5-tap filter can idle by setting the current real tap to 1 and the others to 0.
- **Data.** English DNS4, plus a distortion path: the target keeps less reverberation than the mixture, and clipped speech is reconstructed. That is a meeting-room mechanism, not a guarantee on your rooms.
- **Fewer temporal buffers.** Time kernels shrink from $$2\times 3$$ to $$1\times 3$$ except a causal $$3\times 3$$ at the input. The GRU hidden size is 256. Grouped linears become one matmul. Extra context is a ring of activations; on a small CPU that traffic dominates the MAC count.
- **Post-filter.** A sine warp on the ERB gains, $$G \leftarrow G\sin(\pi G/2)$$, over-attenuates noisy bands. A second step mixes a strength $$\beta$$. Do not invent a default $$\beta$$; `--pf` enables the published post-filter.
- **Same CPU, different RTF.** On Voicebank+Demand, Core i5-8250U: the ICASSP row is 1.778 M parameters, 0.348 GMAC, RTF 0.11, PESQ 2.81. The simplified DF2 row is 2.306 M, 0.356 GMAC, **RTF 0.04**, PESQ 3.08 (CSIG 4.30, CBAK 3.40, COVL 3.699, STOI 0.9429). GMAC is flat; RTF drops because the kernels and the GRU changed. The post-filter row stays at RTF 0.04 and PESQ **3.03**. PESQ fell. Watching only PESQ will revert a change that was made for perception.

The abstract also calls this fast enough for a Raspberry Pi 4. That is still not a phone thermal result.

### The 2023 paper and DeepFilterNet3 — arXiv:2305.08227

“DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement” (Interspeech 2023, arXiv:2305.08227) restates the framework and is the citation the project README associates with the **DeepFilterNet3** model. Use that association. Do not invent a second DF3 title.

The demo’s processing rules, which you can implement without new module names:

- 48 kHz, 20 ms window, 10 ms hop, look-ahead of 2 frames, **40 ms** algorithmic latency.
- 32 ERB gains for the envelope.
- An $$N=5$$ complex filter on the lowest **96 bins** (4.8 kHz). Higher bins keep the ERB gain.
- The encoder also predicts a local SNR $$\xi\in[-15,35]$$ dB. If $$\xi<-10$$ dB, both decoders are disabled and the frame is silent. If $$\xi>20$$ dB, the deep-filter decoder is disabled. Otherwise both stages run.

Speech just under −10 dB becomes digital silence. Speech above 20 dB never gets the harmonic stage, so a hum can remain between partials. The tract loop in that paper reports **RTF 0.19** on one i5-8250U thread. DF2’s **0.04** is a different binary. Do not average them, and do not call either a phone RTF.

The Voicebank+Demand row labeled DeepFilterNet3 is PESQ 3.17, CSIG 4.34, CBAK 3.61, COVL 3.77, STOI 0.944, against DF2 at PESQ 3.08 and the original at 2.81. One test set.

### Wrapper, ONNX, rooms

`deepfilternet3-noise-filter` 1.3.0 ([mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)) runs ONNX/WASM in an AudioWorklet: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, suppression 0–100 via `setSuppressionLevel`. Do not claim bit-exact agreement with the CLI or the paper table. A wrapper that changes hop, look-ahead, or sample rate is a different system.

Export is PyTorch → ONNX → ONNX Runtime, WASM, or tract → AudioWorklet or a native callback. The GRU state must be a graph input and output. A dynamic axis that eats the whole file is an offline model. The first paper’s simulated RT60 stops at 1 s. Over-suppression in a real room is often that data gap. Listen (Chapter 08) before you grow the net.

## Pitfalls

- Loading DF2 weights with the DF3 gate thresholds, or the reverse.
- Quoting PESQ 3.17 as “the product MOS.”
- Treating RTF 0.04 or 0.19 on an i5 as the budget for a fanless laptop or a phone.
- Enabling `--pf`, watching PESQ drop from 3.08 to 3.03, and reverting a perceptual change you never listened to.
- Assuming `setSuppressionLevel(100)` reproduces the paper’s full attenuation. It is a product control, range 0–100, not a dB value from the paper.

## Mini-lab

**Goal.** Run the CLI twice if weights are available, once with the post-filter flag, and always compute the unitless sine warp on four gains so the lab works offline.

```bash
deepFilter --output-dir out/noisy/ noisy.wav
deepFilter --pf --output-dir out/pf/ noisy.wav
python3 - << 'PY'
import numpy as np
G = np.array([0.0, 0.2, 0.5, 1.0])
Gp = G * np.sin(0.5 * np.pi * G)
np.set_printoptions(precision=6, suppress=True)
print(Gp)
PY
```

**Expected**. With weights and a 48 kHz input: two enhanced wavs, and a log that includes timing or RTF. Do not expect the two wavs to match. NumPy always prints `[0. 0.061803 0.353553 1.]`. A gain of 0.2 is pulled down harder than a gain of 1, which is the over-attenuation the post-filter is for. The second, $$\beta$$-weighted, step is intentionally not in this script.

**Failure modes**. No network to download weights: keep the NumPy result and write down the CLI error. A non-48 kHz file into the Rust `deep-filter` binary. Comparing laptop log RTF with a phone. Claiming the `--pf` wav matches `setSuppressionLevel` in the npm package.

## Exercises

1. **Three rows.** For the ICASSP 2022 model, DeepFilterNet2, and the DeepFilterNet3 row, list venue, arXiv id, one mechanism change, and one number you are willing to defend.
2. **Gate.** Local SNR is −12 dB, then +25 dB, then +5 dB. Which stages run?
3. **RTF reading.** DF2’s table says GMAC 0.356 and RTF 0.04; the earlier row says GMAC 0.348 and RTF 0.11. Why can the slower-looking MAC row be faster?
4. **Package.** Name two symbols an app author sees on `deepfilternet3-noise-filter`, and two facts about hops and state the package does not excuse you from knowing.

### Answer hints

1. ICASSP 2022, 2110.05588: two-stage ERB + deep filter; PESQ 2.81 / 1.778 M. IWAENC 2022, 2205.05474: fewer temporal kernels, multi-resolution loss, post-filter; RTF 0.04 and PESQ 3.08 on that i5 table. Interspeech 2023, 2305.08227, README ties this citation to DF3: SNR gate and a table row at PESQ 3.17. All PESQ figures are Voicebank+Demand, not your product set.
2. −12 dB: both decoders off, silent frame. +25 dB: ERB stage only. +5 dB: both stages.
3. MAC tables ignore memory traffic. DF2’s smaller temporal kernels touch fewer buffered activations per hop, which is why RTF moved from 0.11 to 0.04 while GMAC stayed near 0.35.
4. `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, and `setSuppressionLevel` (0–100) are the surface. You still own the 10 ms hop versus the 128-sample quantum, and the GRU/STFT state across callbacks. No bit-exact claim with the CLI.

## Further reading

- Schröter et al., DeepFilterNet2, IWAENC 2022, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474).
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227), the README’s DeepFilterNet3 citation.
- [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) for checkpoints and `deepFilter`.
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) for the AudioWorklet packaging only.
