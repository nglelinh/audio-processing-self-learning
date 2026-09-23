---
layout: post
title: "04-02 DeepFilterNet: deep filtering idea"
chapter: "04"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

**DeepFilterNet** (Schröter et al., ICASSP 2022, arXiv:2110.05588) is a full-band speech enhancer that spends most of its capacity on a coarse auditory envelope and a short complex filter, not on a dense net over all 481 bins. This lesson derives that split, writes the filter sum, and runs it on a two-tap toy spectrum even if the pretrained weights never download.

![DeepFilterNet two-stage diagram: ERB gains on the envelope, deep filter on low-frequency harmonics]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. Stage 1 predicts real gains on 32 ERB bands and applies them to the full STFT. Stage 2 predicts a 5-tap complex filter and applies it only on the low frequencies, where most periodic speech energy sits. High bins keep the ERB gain.*

## Learning objectives

You will compute an ERB gain application and a multi-frame deep-filter sum on complex bins; explain why a 5-tap filter up to about 5 kHz is cheaper than a complex mask on every bin at 48 kHz; state the published STFT (20 ms window, 10 ms hop) and the 40 ms algorithmic delay that includes two frames of look-ahead; and run either the `deepFilter` CLI or the NumPy fallback below.

## 60-minute teaching plan

- **0–10 min** — Why 481 bins at 48 kHz should not all get the same MAC budget.
- **10–25 min** — ERB stage: 32 real gains, pointwise multiply.
- **25–40 min** — Deep-filter sum versus a one-tap Wiener or CRM gain.
- **40–50 min** — Look-ahead, causality, and the official repository.
- **50–60 min** — Mini-lab (CLI or NumPy), exercises.

## Core explanation

### Two stages, with the published sizes

Hearing resolves frequency more finely at low frequency than at high frequency. DeepFilterNet uses that fact twice.

1. **Envelope stage.** A rectangular ERB bank compresses log-power to $$N_{\mathrm{ERB}}=32$$ bands. The net predicts 32 real gains, the inverse bank spreads them onto STFT bins, and they multiply the noisy spectrum. Features use an exponential mean normalization with a 1 s decay, so a microphone-gain jump does not look like a new noise.
2. **Periodicity stage.** Five complex taps run only up to $$f_{\mathrm{DF}}=5$$ kHz (ICASSP and DeepFilterNet2). The 2023 demo (arXiv:2305.08227) says the lowest 96 bins: a 960-point FFT at 48 kHz has 50 Hz bins, and $$96\times 50\,\mathrm{Hz}=4.8$$ kHz. Above the cutoff the ERB gain is the output.

Comparisons use 48 kHz, $$N_{\mathrm{FFT}}=960$$ (20 ms), 50% overlap (hop 480 samples = 10 ms). DeepFilterNet2 and the 2023 demo use a two-frame look-ahead and state **40 ms** algorithmic latency. The ICASSP latency formula is window delay plus $$\max(l_{\mathrm{DNN}}, l_{\mathrm{DF}})$$; the training setup uses $$l_{\mathrm{DNN}}=2$$ and $$l_{\mathrm{DF}}=1$$. Those future frames are delay, counted before anyone says “real time.”

On the VCTK/DEMAND table in the ICASSP paper the full model has 1.778 million parameters and 0.348 GMAC/s, WB-PESQ 2.81, SI-SDR 16.63 dB. Stripping stage 2 leaves 0.885 million parameters, 0.251 GMAC/s, PESQ 2.57, SI-SDR 13.81 dB. Stage 2 is about half the parameters and most of the harmonic restoration.

### The filter is not a mask

A one-tap mask, including the Wiener gain under a Gaussian model, is

$$
\hat{S}(k,\ell)=M(k,\ell)\,Y(k,\ell).
$$

Deep filtering (Mack and Habets, and the CLC line of work the ICASSP paper builds on) predicts taps $$W_i$$ and sums a short history. For a 5-tap filter and an optional look-ahead $$\ell$$,

$$
\hat{S}(t,f)=\sum_{i=0}^{4} W_i(t,f)\,X(t-i+\ell,f).
$$

The ICASSP write-up indexes a filter of order $$N=5$$ as a sum $$\sum_{i=0}^{N}$$; the 2023 demo writes an $$N=5$$ tap vector $$W_0,\ldots,W_{N-1}$$. Teach the five-coefficient sum. Either reading is a per-bin FIR across time, not a per-bin multiply. The lab below uses two taps so the arithmetic fits on one line; the missing three taps are the same pattern.

Complex taps can rotate a bin using a past frame, which a magnitude mask cannot do. Many tap vectors realize one output, so the paper trains them with the compressed spectral loss from 04-01 ($$c=0.6$$), not with a closed-form ideal filter. The ICASSP model also learns a blend $$\alpha(k)$$ between deep-filter output and ERB output. The 2023 demo uses an SNR gate instead (04-03). Do not merge those two mechanisms into one block.

### Why the MAC count falls

The envelope decoder emits 32 gains, not 481 ($$32/481\approx 0.067$$). The fine stage is 5 complex taps on 96 bins, not a CRM on every bin. The ICASSP net also splits linear and GRU layers into $$P=8$$ groups of hidden size $$512/8=64$$. Layer names move between versions; this budget does not.

### Causality and the repository

Taps may only touch frames inside the declared look-ahead. GRU state, the 1 s normalizer, and the past spectra are streaming state (05-04). Zeroing them mid-call is a click or a short noise burst.

Configs and weights: [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet). The `deepfilternet` package’s `deepFilter` CLI defaults to DeepFilterNet3 weights. The Rust `deep-filter` binary expects 48 kHz wav. The npm package `deepfilternet3-noise-filter` ([mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)) runs ONNX/WASM in an AudioWorklet (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`) and is not bit-exact with the CLI.

## Checklist before you call it DeepFilterNet

1. 48 kHz full-band STFT, not a 16 kHz offline net.
2. 32 ERB gains for the envelope.
3. A multi-tap complex filter on the low bins only.
4. Look-ahead counted in the 40 ms class of delay, separately from RTF.
5. Causal state carried across hops.
6. Weights pinned by filename or commit, then exported (Chapter 06).

## Pitfalls

- Calling every mask network “DeepFilterNet.”
- Applying the 5-tap filter to all 481 bins and then wondering where the GMAC budget went.
- Scoring 16 kHz PESQ and claiming the 48 kHz table.
- Forgetting the 20 ms window inside the “10 ms frame” story.
- Swapping DF, DF2, and DF3 checkpoints in one config (next lesson).

## Mini-lab

**Goal.** Enhance one file with the official CLI. If weights cannot download, still compute one deep-filter sum in NumPy and compare it to a one-tap mask.

```bash
pip install deepfilternet
deepFilter --output-dir out/ noisy.wav
```

Documented flags you may need: `--model-base-dir` (local weights), `--pf` (post-filter, lesson 04-03), `--output-dir`, `--compensate-delay`. Input for the Rust `deep-filter` binary is 48 kHz wav.

Offline fallback, two taps of the sum above:

```bash
python3 - << 'PY'
import numpy as np
Y_now = np.complex64(1.0 + 0.5j)
Y_prev = np.complex64(0.2 - 0.1j)
H0 = np.complex64(0.8 + 0.0j)
H1 = np.complex64(0.1 - 0.2j)
deep = H0 * Y_now + H1 * Y_prev
mask = np.complex64(0.8) * Y_now
print(deep)
print(mask)
print(round(abs(deep), 6), round(abs(mask), 6))
PY
```

**Expected**. CLI: an enhanced wav under `out/` and a log line that reports timing or RTF. NumPy, always: deep-filter result `(0.8+0.35j)`, one-tap mask `(0.8+0.4j)`, magnitudes about `0.873212` and `0.894427`. The imaginary part moved because $$H_1$$ used $$Y_{\mathrm{prev}}$$; a mask cannot do that.

**Failure modes**. No network, so the CLI cannot fetch weights — run the NumPy path and record the error, do not invent an output wav. Input that is not 48 kHz into the Rust binary. Reading a laptop RTF off the log and calling it a phone RTF. Forgetting `--output-dir` and then hunting the wav in the wrong folder.

## Exercises

1. **Side by side.** Write the Wiener one-tap gain and the 5-tap sum. Circle learned quantities versus quantities a noise tracker would estimate.
2. **Bins.** At 48 kHz with a 960-point FFT, which bin index is the last one included by a 4.8 kHz cutoff? How many complex taps per frame is that, at 5 taps?
3. **MAC sketch.** The envelope head emits 32 numbers instead of 481. Give the ratio. Why is that not the whole GMAC story?
4. **Delay audit.** Hop 10 ms, look-ahead 2 frames, window 20 ms. What algorithmic latency do you quote, and which CLI flag shifts output alignment rather than that latency?

### Answer hints

1. Wiener: $$M=\xi/(\xi+1)$$, one real (or complex) multiply, $$\xi$$ from a noise tracker. Deep filter: five complex $$W_i$$ from the net, dotted with five frames of $$X$$. Learned: $$W_i$$ and the ERB gains. Estimated in a classical system: $$\xi$$ or the noise PSD.
2. Bin width 50 Hz, so index 96 lands on 4.8 kHz and is the count the 2023 demo uses (“lowest 96 bins”). $$96\times 5=480$$ complex taps per frame, before the high bins, which only receive a real gain.
3. $$32/481\approx 0.0665$$. The STFT, the inverse ERB spread, and the 5-tap multiply on 96 bins are extra. DF2’s lesson is that grouping and kernel shape move wall-clock RTF even when GMAC barely changes.
4. 40 ms. `--compensate-delay` realigns the file for offline scoring; it does not remove the look-ahead from a live call.

## Further reading

- Schröter et al., ICASSP 2022, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588). ERB gains, deep filtering, the 1.778 M / 0.348 GMAC table.
- Mack and Habets, “Deep Filtering,” IEEE Signal Processing Letters, 2020, as cited by that paper: the complex multi-frame filter DeepFilterNet adopts.
- [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) README for the `deepFilter` CLI and the model card.
- Next lesson: what DeepFilterNet2 and the DeepFilterNet3-associated 2023 citation change, at the same high level.
