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

![DFT basis tones drawn as the discrete grid the FFT actually evaluates]({{ site.imgurl }}/generated/dft-basis.png)

*Figure. A DFT does not draw a continuous curve; it reports inner products against these discrete complex tones, one bin per tone.*

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

Interpretation that prevents bugs: **DFT values are samples of the DTFT** of the finite sequence (zero outside the block) at \(\omega_k=2\pi k/N\), equivalently samples of the DTFT of the periodic extension. Write the DTFT sum, then restrict the frequency:

$$
X(e^{j\omega})\Big|_{\omega=2\pi k/N}
=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
=X[k].
$$

Nothing in that substitution invents new information between the bins. Multiplying two DFTs ↔ **circular** convolution of length \(N\), not linear convolution — hence overlap-save/overlap-add methods for long filters.

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

Take 64 samples of a 1 kHz tone at 16 kHz. The tone completes \(1000\times 64/16000=4\) cycles, so the length-64 DFT peaks at bin 4. Pad to 512 and the same 64 samples peak at bin \(1000\times 512/16000=32\). Bin spacing changed from \(16000/64=250\,\mathrm{Hz}\) to \(16000/512=31.25\,\mathrm{Hz}\), but the main lobe in hertz is still set by the 64-sample observation, about 250 Hz wide, not by 31.25 Hz. The mini-lab prints those two peak indices. At the 48 kHz product default, the same trap appears when someone zero-pads a 10 ms frame and calls the new bin spacing “better pitch resolution” without lengthening the window the mic actually filled.

## Common pitfalls

1. Marketing zero-padding as super-resolution.
2. Forgetting circular vs linear convolution.
3. Comparing \(|X[k]|\) across different \(N\) without normalization.
4. Breaking conjugate symmetry then taking “real” iFFT (imag leftovers = bugs).
5. Changing \(N\) between training and inference for a neural masker.

## Mini-lab

**Goal.** Compare a 64-point DFT of a 1 kHz tone at 16 kHz with the same 64 samples zero-padded to 512.

```python
import numpy as np

fs, n_win = 16_000, 64
n = np.arange(n_win)
tone = np.cos(2 * np.pi * 1000 * n / fs)
peak64 = int(np.argmax(np.abs(np.fft.rfft(tone))))
peak512 = int(np.argmax(np.abs(np.fft.rfft(tone, n=512))))
print(peak64, peak512, fs / n_win, fs / 512)
```

**Expected.** `4 32 250.0 31.25`. The peak index moved because the grid got denser. The observation length did not.

**Failure modes.** Reading bin 32 at \(N=512\) as “the tone got sharper.” Comparing raw `|rfft|` peak heights across the two lengths without a scale convention. Forgetting that a cosine at an integer bin also has a negative-frequency twin that `rfft` does not print separately.

## Mini exercises

1. Nearest bin to 1 kHz at \(f_s=16\,\mathrm{kHz}\), \(N=512\).
2. One sentence: zero-pad vs longer window.
3. On-bin vs half-bin tone: which leaks more with a rectangular window?
4. Why does STFT use hop \(R<N\) instead of adjacent non-overlapping DFTs only?
5. If weights expect 513 magnitude bins, what \(N\) is implied for a real FFT?

### Answer hints

1. \(\Delta f=16000/512=31.25\,\mathrm{Hz}\), so 1 kHz is bin \(1000/31.25=32\) exactly.
2. Zero-padding densifies samples of the same DTFT. A longer window narrows the main lobe.
3. An on-bin tone matches one basis vector and, with a rectangular window, sits in one bin. A half-bin tone is discontinuous under periodic extension and leaks.
4. Hop \(R<N\) is what builds overlap so the inverse STFT can satisfy constant overlap-add. Adjacent DFTs with \(R=N\) leave a rectangular splice.
5. A packed real FFT keeps \(N/2+1\) bins, so 513 bins means \(N=1024\).

## Further reading

- Oppenheim & Schafer — relationships among DTFT/DFS/DFT.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — DFT, DTFT, and zero-padding.
- DeepFilterNet (arXiv:2110.05588) and the reference repo https://github.com/Rikorose/DeepFilterNet for the frame length the weights actually saw. RNNoise’s public docs are the classical comparison for a smaller FFT.
