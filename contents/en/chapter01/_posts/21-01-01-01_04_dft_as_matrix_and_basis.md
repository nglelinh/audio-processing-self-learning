---
layout: post
title: "01-04 DFT as matrix / orthonormal basis"
chapter: "01"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

Debugging NS requires treating the DFT as a change of basis with a known metric (Parseval), not as a colorful plot. This lesson connects orthogonality, matrix form, bin indexing, and leakage.

## Learning objectives

1. View the DFT as projection onto complex exponentials.
2. Write the DFT as a matrix acting on vectors; know unitary vs unnormalized conventions.
3. Apply Parseval-type energy checks when validating STFT/ISTFT.
4. Convert among bin index, Hz, and normalized frequency fluently.
5. Predict and recognize off-bin spectral leakage.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Orthogonal exponentials; inner-product view |
| 12–28 | Matrix \(\mathbf{F}\); unitary scaling; library conventions |
| 28–42 | Bin↔Hz drills; DC/Nyquist; negative frequencies |
| 42–52 | Off-bin leakage; tone+noise lab sketch |
| 52–60 | Exercises / checklist |

## Core explanations

### Analysis as inner products

Basis vectors \(w_k[n]=e^{j2\pi kn/N}\) satisfy

$$
\langle w_k,w_\ell\rangle=\sum_{n=0}^{N-1}w_k[n]w_\ell[n]^*=N\delta_{k\ell}
$$

DFT analysis: \(X[k]=\langle x,w_k\rangle\) (with conjugation conventions matching the forward sign). Synthesis: rebuild \(x\) from coefficients. This is why modifying \(X[k]\) is surgery in a coordinate system — illegal surgery (breaking symmetries, inconsistent hop windows) shows up as time-domain garbage.

### Matrix form

$$
\mathbf{X}=\mathbf{F}\mathbf{x},\quad F_{kn}=e^{-j2\pi kn/N}
$$

Unitary DFT \(\mathbf{U}=\mathbf{F}/\sqrt{N}\) obeys \(\mathbf{U}^H\mathbf{U}=\mathbf{I}\) and preserves \(\|\mathbf{x}\|_2\). Many FFT APIs use unnormalized forward + \(1/N\) inverse (or the opposite). **ISTFT scaling bugs** are among the top silent quality killers: output too quiet/loud, or OLA not COLA-normalized.

### Frequency axis

$$
f_k=\frac{k}{N}f_s,\quad k=0,1,\ldots,\lfloor N/2\rfloor
$$

- \(k=0\): DC (mean).
- \(k=N/2\) (even \(N\)): Nyquist.
- \(k>N/2\): negative frequencies for real signals (\(k\leftrightarrow k-N\)).

### Parseval (unnormalized DFT common form)

$$
\sum_{n}|x[n]|^2=\frac{1}{N}\sum_{k}|X[k]|^2
$$

Use this to unit-test your STFT→ISTFT round trip on random vectors (with windows/hop accounted for).

### Leakage

A sinusoid whose frequency is not an integer number of cycles inside the DFT block is discontinuous under periodic extension → spectral sidelobes. Windows taper edges (Ch. 02) to reduce sidelobes at the cost of main-lobe width.

## Worked examples

### Mapping

\(f_s=48\,\mathrm{kHz}\), \(N=1024\), \(\Delta f\approx46.875\,\mathrm{Hz}\). HVAC ~100 Hz → near bins 2–3. A mask that only zeros bin 2 but leaves 3–10 may do little; smooth gains across neighbors.

### Energy check

Unit-variance white noise length 256: time energy \(\approx256\). Unnormalized DFT energy sum_k |X|^2 ≈ \(256\cdot256=65536\), so divide by \(N=256\) to match Parseval.

### Tone + noise

On-bin tone: single spike (rectangular window). Add white noise: floor rises. Classical Wiener gain \(\approx \frac{P_s}{P_s+P_n}\) per bin rides on estimating those powers — neural masks learn similar ideas with more context.

## Common pitfalls

1. Double \(1/N\).
2. Displaying mirrored spectrum as if unique content doubled.
3. Editing half-spectrum without conjugate mirror.
4. Comparing different FFT norms across languages (NumPy vs FFTW vs Rust libs).
5. Using `|X|**2` without window power normalization when estimating PSD.

## Mini exercises

1. For \(N=4\), write \(\mathbf{F}\) explicitly.
2. \(k=32\), \(f_s=16\,\mathrm{kHz}\), \(N=256\) → Hz?
3. Why do off-bin tones look broadband under rectangular windows?
4. Design a 5-line unit test for Parseval on your FFT wrapper.
5. If DC bin is huge, what time-domain symptom do you expect?

## Further reading

- Oppenheim & Schafer — DFT properties, Parseval, eigenreading of DFT.
- Library docs for your FFT (normalization flags).
- Speech STFT tutorials discussing scaling and window power.
