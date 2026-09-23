---
layout: post
title: "02-03 Windowing and spectral leakage"
chapter: "02"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Windows control the tradeoff between spectral leakage and main-lobe width. In NS, the wrong window (or mismatched analysis/synthesis pair) creates musical noise and hop-rate warble.

## Learning objectives

1. Explain spectral leakage from rectangular truncation.
2. Compare common windows (Hann, Hamming, Blackman) qualitatively.
3. Connect main-lobe width to frequency resolution and time localization.
4. State how windows interact with COLA and NS masking.
5. Choose windows consistently with a pretrained STFT front-end.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Rectangular window leakage demo (thought/plot) |
| 12–28 | Window catalog; sidelobe vs main lobe |
| 28–42 | COLA + window choice; doubling windows |
| 42–52 | Musical noise link to bin independence myth |
| 52–60 | Exercises |

## Core explanations

### Leakage mechanism

Multiplying by \(w[n]\) convolves the DTFT with \(W(e^{j\omega})\). Rectangular \(w\) has high sidelobes → distant bins contaminated. Tapered windows lower sidelobes, widen main lobe → nearby bins blurred together.

### Qualitative comparison

| Window | Sidelobes | Main lobe | Notes |
|--------|-----------|-----------|-------|
| Rectangular | poor | narrowest | analysis curiosity |
| Hann | good | wider | STFT favorite; COLA @ 50% common |
| Hamming | similar | similar | sidelobe floor differs |
| Blackman | lower sidelobes | wider | more smoothing |

Exact coefficients are standard; copy from a DSP reference when implementing — do not invent.

### Resolution tradeoff

Effective frequency resolution \(\sim \alpha f_s/L\) with \(\alpha>1\) depending on window. Time localization \(\sim L/f_s\). Speech NS wants enough resolution to separate formants/noise floors, enough time locality for consonants — hence mid-length windows (tens of ms), not 1 ms and not 1 s.

### Windows and masks

Neural/classical gains that jump wildly across adjacent bins fight the window’s inherent smoothing — or create musical noise when bins are treated as independent. Smooth masks in frequency (and time) match physics better.

### Analysis vs synthesis

Some pipelines use \(w\) on analysis only and a different synthesis window for COLA. Others use \(\sqrt{\text{Hann}}\) on both (power complementary designs). **Match training.** Randomly switching to Blackman “for quality” breaks reconstruction.

## Worked examples

### On-bin vs off-bin

16 kHz, \(L=512\), tone exactly bin 32 vs bin 32.5. Rectangular: off-bin spreads widely. Hann: sidelobes drop, main lobe wider — both bins 32 and 33 light up.

### Musical noise

Spectral subtraction with independent bin floors → isolated bin spikes surviving as birdies. Over-smoothing helps but blurs speech — classic tension before neural SE.

## Common pitfalls

1. Applying window twice unintentionally (pre-windowed API + manual window).
2. Using rectangular for NS because “FFT needs it.”
3. Ignoring window gain when checking Parseval / SI-SDR.
4. Different windows in train vs serve.
5. Expecting window alone to fix aliasing (it will not).

## Mini exercises

1. Why do tapered windows reduce sidelobes?
2. If \(L\) doubles, what happens to main-lobe width roughly?
3. Name a COLA-friendly hop for Hann (common choice).
4. How can aggressive per-bin masks create musical noise?
5. Give one reason \(\sqrt{\text{Hann}}\) appears in STFT codebases.

## Further reading

- Oppenheim & Schafer — windows and spectral analysis.
- Standard window comparison notes (DSP course handouts).
- DeepFilterNet STFT configuration sections.
