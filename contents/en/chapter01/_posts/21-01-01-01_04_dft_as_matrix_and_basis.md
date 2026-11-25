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

If you only ever think of an FFT as a black box that spits out a pretty spectrogram, one subtle scaling mismatch between Python (`numpy.fft`) and C++/Rust (`FFTW` / `realfft`) will silently drain your audio by $$10\times$$—or blow it up into harsh clipping.

The cleanest cure is linear algebra: **the length-$$N$$ DFT is simply a rotation into an orthogonal basis**, represented by a single $$N \times N$$ Vandermonde matrix $$\mathbf{F}$$. Once you view `fft(x)` as $$\mathbf{X} = \mathbf{F}\mathbf{x}$$, Parseval’s energy check becomes a one-line unit test, conjugate symmetry becomes obvious, and spectral leakage stops looking mysterious.

![Eight DFT basis tones: the coordinates a length-N transform uses]({{ site.imgurl }}/generated/dft-basis.png)

*Figure. Each row of the DFT matrix is one of these complex tones; a bin is the inner product of the frame with that row.*

**Lesson roadmap:** Key ideas (orthogonal complex exponentials, unitary vs. unnormalized scaling, Parseval’s theorem) → Matrix form, frequency axis, and leakage → Worked examples: length-4 DFT of $$x = [1, 0, -1, 0]$$ checked by hand against Parseval, 48 kHz bin mapping, and white-noise energy check → Explanation: 3 steps turning orthogonality into your STFT/ISTFT unit tests → Pitfalls, Mini-lab, Exercises & Videos.

---

## Key ideas: Linear Algebra of the Discrete Fourier Transform

### 1. Orthogonal Basis in $$\mathbb{C}^N$$
The $$N$$ complex exponential vectors $$w_k[n] = e^{j2\pi kn/N}$$ ($$k = 0, \ldots, N-1$$) are mutually perpendicular in $$\mathbb{C}^N$$: $$\langle w_k, w_\ell \rangle = N\delta_{k\ell}$$. Taking a DFT is literally projecting your audio frame $$\mathbf{x}$$ onto these $$N$$ perpendicular axes.

### 2. Unitary Scaling vs. Library Scaling Conventions
Dividing $$\mathbf{F}$$ by $$\sqrt{N}$$ yields a **unitary matrix** $$\mathbf{U} = \mathbf{F}/\sqrt{N}$$ satisfying $$\mathbf{U}^H \mathbf{U} = \mathbf{I}$$, which preserves vector length identically ($$\Vert \mathbf{Ux}\Vert_2 = \Vert \mathbf{x}\Vert_2$$). Most numerical libraries (NumPy, FFTW, kissfft) avoid $$\sqrt{N}$$ for speed: they put factor $$1$$ on the forward transform and $$1/N$$ on the inverse (or expect *you* to divide by $$N$$). Forgetting which convention your library uses is one of the top silent bugs in streaming audio!

### 3. On-Bin Tones vs. Off-Bin Spectral Leakage
A sinusoid that completes an exact integer number of cycles inside $$N$$ samples aligns with a single basis vector $$w_k$$, putting 100% of its energy into one bin (plus its conjugate twin). Any fractional-cycle sinusoid sits *between* basis axes—its projection spills non-zero coefficients across all $$N$$ bins (**spectral leakage**).

---

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
| 12–28 | Matrix $$\mathbf{F}$$; unitary scaling; library conventions |
| 28–42 | Bin↔Hz drills; DC/Nyquist; negative frequencies |
| 42–52 | Off-bin leakage; tone+noise lab sketch |
| 52–60 | Exercises / checklist |

## Core explanations

### Analysis as inner products

Basis vectors $$w_k[n]=e^{j2\pi kn/N}$$ satisfy

$$
\langle w_k,w_\ell\rangle=\sum_{n=0}^{N-1}w_k[n]w_\ell[n]^*=N\delta_{k\ell}
$$

DFT analysis: $$X[k]=\langle x,w_k\rangle$$ (with conjugation conventions matching the forward sign). One check of the inner-product claim: the geometric sum $$\sum_{n=0}^{N-1}e^{j2\pi(k-\ell)n/N}$$ equals $$N$$ when $$k\equiv\ell\pmod N$$ and equals 0 otherwise, which is exactly $$\langle w_k,w_\ell\rangle=N\delta_{k\ell}$$. Synthesis divides by that $$N$$. This is why modifying $$X[k]$$ is surgery in a coordinate system — illegal surgery (breaking symmetries, inconsistent hop windows) shows up as time-domain garbage.

**From unitary to the library’s $$1/N$$.** Let $$\mathbf{U}=\mathbf{F}/\sqrt{N}$$. Orthonormality says $$\|\mathbf{Ux}\|_2=\|\mathbf{x}\|_2$$. The unnormalized forward transform used by NumPy’s default `fft` is $$\mathbf{X}=\mathbf{Fx}=\sqrt{N}\,\mathbf{Ux}$$, so

$$
\sum_k\vert X[k]\vert^2=N\sum_n\vert x[n]\vert^2
\quad\Rightarrow\quad
\sum_n\vert x[n]\vert^2=\frac{1}{N}\sum_k\vert X[k]\vert^2.
$$

If your streaming inverse divides by $$N$$ and the overlap-add path divides by $$N$$ again, a 48 kHz full-band waveform gets quieter on every hop. `setSuppressionLevel` on `DeepFilterNoiseFilterProcessor` does not audit that bug: the slider scales suppression, it does not check Parseval in a hand-written STFT sitting beside the package.

### Matrix form

$$
\mathbf{X}=\mathbf{F}\mathbf{x},\quad F_{kn}=e^{-j2\pi kn/N}
$$

Unitary DFT $$\mathbf{U}=\mathbf{F}/\sqrt{N}$$ obeys $$\mathbf{U}^H\mathbf{U}=\mathbf{I}$$ and preserves $$\|\mathbf{x}\|_2$$. Many FFT APIs use unnormalized forward + $$1/N$$ inverse (or the opposite). **ISTFT scaling bugs** are among the top silent quality killers: output too quiet/loud, or OLA not COLA-normalized.

### Frequency axis

$$
f_k=\frac{k}{N}f_s,\quad k=0,1,\ldots,\lfloor N/2\rfloor
$$

- $$k=0$$: DC (mean).
- $$k=N/2$$ (even $$N$$): Nyquist.
- $$k>N/2$$: negative frequencies for real signals ($$k\leftrightarrow k-N$$).

### Parseval (unnormalized DFT common form)

$$
\sum_{n}\vert x[n]\vert^2=\frac{1}{N}\sum_{k}\vert X[k]\vert^2
$$

Use this to unit-test your STFT→ISTFT round trip on random vectors (with windows/hop accounted for).

### Leakage

A sinusoid whose frequency is not an integer number of cycles inside the DFT block is discontinuous under periodic extension → spectral sidelobes. Windows taper edges (Ch. 02) to reduce sidelobes at the cost of main-lobe width.

## Worked examples

### Mapping

$$f_s=48\,\mathrm{kHz}$$, $$N=1024$$, $$\Delta f\approx46.875\,\mathrm{Hz}$$. HVAC ~100 Hz → near bins 2–3. A mask that only zeros bin 2 but leaves 3–10 may do little; smooth gains across neighbors.

### Energy check

Unit-variance white noise length 256: time energy $$\approx256$$. Unnormalized DFT energy $$\sum_k\vert X[k]\vert^2\approx 256\cdot 256=65536$$, so divide by $$N=256$$ to match Parseval.

### On-bin cosine, $$N=4$$

Let $$x=[1,0,-1,0]$$, which is $$\cos(2\pi n/4)$$: one cycle in four samples, so it is exactly basis bin $$k=1$$. Multiply by the $$4\times 4$$ DFT matrix $$\mathbf{F}$$ (where $$F_{kn} = (-j)^{kn}$$):
- $$X[0] = 1 + 0 - 1 + 0 = 0$$
- $$X[1] = 1 + 0 - (-1)(-1) + 0 = 1 - (-1) = 2$$
- $$X[2] = 1 + 0 - 1 + 0 = 0$$
- $$X[3] = 1 + 0 - (-1)(-1) + 0 = 2$$

Time energy is $$1^2+0^2+(-1)^2+0^2=2$$. Frequency energy is $$(0^2+2^2+0^2+2^2)/4=8/4=2$$—exact Parseval match! Exercise 1 still asks you to write the whole matrix; this walk-through checks the two peaks and Parseval. Off-bin tones do not collapse to two spikes — that is leakage, and a rectangular window makes it obvious.

### Tone + noise

On-bin tone: single spike (rectangular window). Add white noise: floor rises. Classical Wiener gain $$\approx \frac{P_s}{P_s+P_n}$$ per bin rides on estimating those powers — neural masks learn similar ideas with more context.

---

### Explanation: Turning Orthogonality into Rock-Solid FFT Unit Tests

#### Step 1: Verify orthogonality via the finite geometric sum
For $$k \neq \ell$$, let $$r = e^{j2\pi(k-\ell)/N} \neq 1$$. Because $$r^N = e^{j2\pi(k-\ell)} = 1$$, the geometric series collapses identically to zero:
$$
\langle w_k, w_\ell \rangle = \sum_{n=0}^{N-1} r^n = \frac{1 - r^N}{1 - r} = 0.
$$
When $$k = \ell$$, every term is $$1$$, summing to $$N$$. That single identity proves $$\mathbf{F}^H\mathbf{F} = N\mathbf{I}$$—meaning the inverse DFT is literally $$\mathbf{F}^{-1} = \frac{1}{N}\mathbf{F}^H$$!

#### Step 2: Catch cross-language FFT scaling bugs with Parseval
Before plugging an FFT wrapper (FFTW in C++, `rustfft` in Rust, or WebAssembly) into your audio graph, run one random real vector through it and check $$\sum \vert X[k]\vert^2 / N \approx \sum \vert x[n]\vert^2$$. If they differ by $$N$$ or $$\sqrt{N}$$, you caught a normalization mismatch in 5 lines of code.

#### Step 3: Enforce Hermitian symmetry whenever editing complex bins
If your neural mask or filter modifies bin $$k$$ ($$1 \le k < N/2$$) in a full complex FFT, you *must* apply the conjugate modification to bin $$N - k$$ (and keep DC $$k=0$$ and Nyquist $$k=N/2$$ purely real), or use a dedicated `irfft` that handles mirroring automatically.

Summary of the matrix DFT toolkit:

$$
\mathbf{X} = \mathbf{F}\mathbf{x}
\;\xrightarrow{\mathbf{F}^H\mathbf{F} = N\mathbf{I}}\;
\mathbf{x} = \frac{1}{N}\mathbf{F}^H\mathbf{X}
\;\Longrightarrow\;
\sum_n \vert x[n]\vert^2 = \frac{1}{N}\sum_k \vert X[k]\vert^2.
$$

## Common pitfalls

1. Double $$1/N$$.
2. Displaying mirrored spectrum as if unique content doubled.
3. Editing half-spectrum without conjugate mirror.
4. Comparing different FFT norms across languages (NumPy vs FFTW vs Rust libs).
5. Using `|X|**2` without window power normalization when estimating PSD.

## Mini-lab

**Goal.** Build a length-8 DFT matrix and check conjugate symmetry and Parseval on one real vector.

```python
import numpy as np

N = 8
n = np.arange(N)
F = np.exp(-2j * np.pi * np.outer(n, n) / N)
x = np.array([1.0, -0.5, 0.25, 0.0, 0.1, -0.2, 0.3, -0.1])
X = F @ x
sym = np.max(np.abs(X - np.conj(X[(N - n) % N])))
energy_time = np.sum(np.abs(x) ** 2)
energy_freq = np.sum(np.abs(X) ** 2) / N
print(f"sym={sym:.3e}")
print(f"time={energy_time:.6f} freq={energy_freq:.6f}")
```

**Expected.** `sym` below `1e-12` (about `1.200e-15`). Both energies print `1.462500`.

**Failure modes.** Using $$e^{+j2\pi kn/N}$$ and comparing to `numpy.fft.fft` without a sign note (this lab does not call NumPy’s FFT; the symmetry and Parseval checks still hold for this $$F$$). Forgetting the `/ N` in Parseval and “fixing” it by dividing the time energy instead. Editing `X[1]` and not its conjugate partner `X[7]`, then expecting a real inverse.

## Mini exercises

1. For $$N=4$$, write $$\mathbf{F}$$ explicitly.
2. $$k=32$$, $$f_s=16\,\mathrm{kHz}$$, $$N=256$$ → Hz?
3. Why do off-bin tones look broadband under rectangular windows?
4. Design a 5-line unit test for Parseval on your FFT wrapper.
5. If DC bin is huge, what time-domain symptom do you expect?

### Answer hints

1. Row $$k$$, column $$n$$ is $$e^{-j2\pi kn/4}$$. Row 0 is all ones. Row 2 is $$[1,-1,1,-1]$$.
2. $$f=32\times 16000/256=2000\,\mathrm{Hz}$$.
3. Periodic extension jumps at the block edge, so the tone is not one basis vector. The rectangular window’s sinc spreads it.
4. Draw a real vector, compare $$\sum\vert x\vert^2$$ with $$(\sum\vert X\vert^2)/N$$, and assert the absolute gap is under `1e-6` for your FFT’s documented scale.
5. A large DC bin is a large mean. The waveform sits off zero; a DC blocker or a bias in the mic path is the first place to look.

## Further reading

- Oppenheim & Schafer — DFT properties, Parseval, eigenreading of DFT.
- Library docs for your FFT (normalization flags).
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — the DFT matrix, orthogonality, and Parseval.

## Video tham khảo

- [Computing the DFT Matrix](https://www.youtube.com/watch?v=Xw4voABxU5c) — Steve Brunton, English. **xem trước.** This is the matrix whose rows are the complex tones. Watch how a bin is one inner product, which is the change of basis in the lesson.
- [The Discrete Fourier Transform (DFT)](https://www.youtube.com/watch?v=nl9TZanwbBk) — Steve Brunton, English. The opening derives that matrix multiplication before any FFT speedup, which is the object this lesson asks you to debug with.
- [Chương 3.1: Biến đổi Fourier rời rạc (DFT)](https://www.youtube.com/watch?v=bC5umvKV8bE) — Tín hiệu và hệ thống UEt, Vietnamese. Vietnamese walk-through of the DFT sum. Pair it with the matrix video when the bin index is the thing that breaks.
