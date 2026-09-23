---
layout: post
title: "01-03 DTFT, DFS, and DFT relationships"
chapter: "01"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

Production audio never computes an infinite DTFT sum. It computes finite DFTs (via FFTs) on windows, hop after hop. This lesson builds the map: DTFT ↔ DFS ↔ DFT, so STFT hyperparameters become meaningful.

## Learning objectives

1. Distinguish DTFT (discrete time, continuous frequency) from DFT (finite grid).
2. Explain periodicity relationships among time and frequency without full proofs.
3. Interpret DFT bins as samples of a windowed segment’s spectrum.
4. Contrast zero-padding with true frequency resolution.
5. Use conjugate symmetry and explain why NS stacks cite “N-point FFT” frames.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Taxonomy of transforms; where STFT sits |
| 12–28 | DTFT definition; windowing as spectral convolution |
| 28–42 | DFT formulas; zero-padding experiment design |
| 42–52 | Real symmetry; circular convolution warning |
| 52–60 | Exercises tied to DeepFilterNet-style N choices |

## Core explanations

### Transform zoo (engineer edition)

| Name | Time domain | Frequency domain | In NS code? |
|------|-------------|------------------|-------------|
| CTFT | continuous | continuous | theory |
| DTFT | infinite discrete | continuous, \(2\pi\)-periodic | theory / math |
| DFS | periodic discrete | periodic discrete | rare by name |
| DFT/FFT | length-\(N\) vector | \(N\) bins | **everywhere** |
| STFT | windowed frames | DFT per frame | **NS backbone** |

### DTFT

$$
X(e^{j\omega})=\sum_{n=-\infty}^{\infty}x[n]e^{-j\omega n},\qquad
x[n]=\frac{1}{2\pi}\int_{-\pi}^{\pi}X(e^{j\omega})e^{j\omega n}\,\mathrm{d}\omega
$$

\(\omega\) is normalized radians/sample. Physical Hz needs \(f_s\).

### DFT

For \(x[0],\ldots,x[N-1]\):

$$
X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
$$

$$
x[n]=\frac{1}{N}\sum_{k=0}^{N-1}X[k]e^{j2\pi kn/N}
$$

Interpretation that prevents bugs: **DFT values are samples of the DTFT** of the finite sequence (zero outside the block) at \(\omega_k=2\pi k/N\), equivalently samples of the DTFT of the periodic extension. Multiplying two DFTs ↔ **circular** convolution of length \(N\), not linear convolution — hence overlap-save/overlap-add methods for long filters.

### Windowing = frequency-domain smearing

Rectangular truncation to length \(L\) multiplies by a window \(w[n]\), convolving \(X(e^{j\omega})\) with \(W(e^{j\omega})\). Main lobe width scales like \(1/L\). That is why 5 ms windows cannot separate 50 Hz pitch harmonics cleanly, while 40 ms windows blur plosive timing.

### Zero-padding ≠ magic resolution

Pad length-\(L\) data to \(N>L\) zeros:

- DFT samples the *same* underlying DTFT more densely.
- Peak locations interpolate more smoothly.
- Two close tones under one main lobe remain unresolvable.

Need finer true resolution → longer coherent observation (larger \(L\)), paying latency and non-stationarity.

### Conjugate symmetry (real PCM)

$$
X[k]=X^*[N-k]
$$

Unique info in \(0\le k\le N/2\). Real-FFT packing stores roughly \(N/2+1\) complex bins. If your mask network outputs \(N/2+1\) magnitudes, mirror before iFFT — or use a library that expects packed format.

### Typical N in speech NS

Orders of magnitude seen in RNNoise / DeepFilterNet-class systems: hundreds to ~1024 bins depending on rate and window. Always read the **specific** paper or config: wrong \(N\) breaks pretrained weights.

Example: \(f_s=48\,\mathrm{kHz}\), \(N=960\) (exactly 20 ms if hop framing aligns). \(\Delta f=50\,\mathrm{Hz}\). At 16 kHz, \(N=512\) ⇒ \(\Delta f=31.25\,\mathrm{Hz}\).

## Worked examples

### Bin listing

\(f_s=16\,\mathrm{kHz}\), \(N=512\). Bin \(k \leftrightarrow k\cdot 31.25\,\mathrm{Hz}\). Speech fundamental 120 Hz ≈ bin 3.84 → energy spreads over bins 3–5 due to window lobe — masks should be smoothed.

### Circular convolution trap

Multiply DFT of signal by DFT of a long FIR reverb impulse truncated poorly into \(N\) taps: time-domain wrap creates metallic pre-echoes. Use OLA with sufficient FFT size \(N \ge L_x+L_h-1\) for linear convolution blocks.

### Zero-pad demo design

Take 64 samples of a 1 kHz tone at 16 kHz; DFT 64 vs pad to 512. The 512-point plot looks smoother but the lobe width in Hz is still governed by the 64-sample observation (~250 Hz-scale lobe), not by 512.

## Common pitfalls

1. Marketing zero-padding as super-resolution.
2. Forgetting circular vs linear convolution.
3. Comparing \(|X[k]|\) across different \(N\) without normalization.
4. Breaking conjugate symmetry then taking “real” iFFT (imag leftovers = bugs).
5. Changing \(N\) between training and inference for a neural masker.

## Mini exercises

1. Nearest bin to 1 kHz at \(f_s=16\,\mathrm{kHz}\), \(N=512\).
2. One sentence: zero-pad vs longer window.
3. On-bin vs half-bin tone: which leaks more with a rectangular window?
4. Why does STFT use hop \(R<N\) instead of adjacent non-overlapping DFTs only?
5. If weights expect 513 magnitude bins, what \(N\) is implied for a real FFT?

## Further reading

- Oppenheim & Schafer — relationships among DTFT/DFS/DFT.
- Classic DSP course notes on windowing and resolution.
- DeepFilterNet / RNNoise documentation of frame FFT sizes.
