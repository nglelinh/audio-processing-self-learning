---
layout: post
title: "01-05 FFT algorithms and complexity"
chapter: "01"
order: 5
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter01
lesson_type: required
draft: false
---

Multiplying an $$N \times N$$ DFT matrix by a 1024-sample audio frame takes over a **million** complex multiply-adds—every single hop, twice (forward and inverse), a hundred times a second. On a phone CPU or inside a browser AudioWorklet, that naive $$O(N^2)$$ cost burns your real-time budget before the neural network even starts.

Enter the **Fast Fourier Transform (FFT)**: not a new transform, not an approximation, but a breathtaking algebraic factorization (rediscovered by Cooley and Tukey in 1965, traced back to Gauss in 1805!) that computes the *exact same* DFT in $$O(N \log N)$$ operations—cutting $$1{,}048{,}576$$ ops down to roughly $$10{,}240$$. This lesson unpacks how the butterfly split works, why real-FFT and mixed-radix sizes like $$960 = 2^6 \cdot 3 \cdot 5$$ matter in DeepFilterNet, and what production rules keep FFTs fast on live audio threads.

![The same DFT basis tones an FFT evaluates; the algorithm changes the schedule, not the tones]({{ site.imgurl }}/generated/dft-basis.png)

*Figure. Radix-2 still computes inner products against these basis tones. It only changes the order of the arithmetic, which is why the result matches a naive DFT up to roundoff.*

**Lesson roadmap:** Background Knowledge Map (divide-and-conquer factorization, twiddle symmetries, real & mixed-radix FFTs) → Radix-2 Cooley–Tukey butterflies & complexity table → Practical production rules (plan reuse, zero-alloc, SIMD) → Worked examples: 10 ms hop ops budget, padding 960 → 1024, and a 4-point butterfly checked by hand → Deep-Dive Explanation (Read Slowly): 3 steps from the even/odd split to $$O(N\log N)$$ → Pitfalls, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: Fast Algorithms for the DFT

### 1. Same Mathematics, Smarter Factorization
The FFT does not change a single output number of the DFT (up to floating-point roundoff $$\sim 10^{-14}$$). It exploits the periodicity and symmetry of roots of unity $$W_N^k = e^{-j2\pi k/N}$$ to factor the dense $$N\times N$$ matrix $$\mathbf{F}$$ into $$\log_2 N$$ ultra-sparse **butterfly stages**.

### 2. Real-Input and Mixed-Radix FFTs
Two optimizations matter constantly in speech pipelines:
- **Real FFT (`rfft`):** Since audio PCM is real, conjugate symmetry cuts the arithmetic roughly in **half**.
- **Mixed-radix FFT:** You do *not* need $$N$$ to be a power of 2! A 20 ms frame at 48 kHz has $$N = 960 = 2^6 \cdot 3 \cdot 5$$—smooth small prime factors that mixed-radix libraries (`pocketfft`, `rustfft`, `FFTW`) run almost as fast as $$N = 1024$$ without altering bin frequencies!

### 3. Audio-Thread Engineering: Plans, Allocations, and SIMD
Asymptotic $$O(N\log N)$$ is only half the story. In production, allocating scratch buffers or recomputing twiddle tables inside a 10 ms callback will blow past your deadline. Always precompute FFT plans once at startup, preallocate workspaces, and enable SIMD (WASM SIMD / NEON / AVX).

---

## Learning objectives

1. Explain why FFT is $$O(N\log N)$$ versus naive $$O(N^2)$$ DFT.
2. Describe radix-2 Cooley–Tukey divide-and-conquer at a cartoon level.
3. List practical constraints: power-of-two sizes, real-FFT optimizations, plan reuse.
4. Estimate FFT cost relative to neural ops in a hop budget.
5. Know what “calling FFT” means inside ONNX graphs vs hand-written WASM.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Complexity arithmetic: $$N=1024$$ naive vs FFT ops order |
| 10–28 | Radix-2 butterfly idea; bit reversal awareness |
| 28–42 | Real FFT packing; non-power-of-two Bluestein/mixed radix (awareness) |
| 42–52 | Library landscape: native, WASM SIMD, ORT FFT ops |
| 52–60 | Exercises |

## Core explanations

### Naive cost

Each of $$N$$ outputs sums $$N$$ complex multiply-adds → $$\Theta(N^2)$$. For $$N=1024$$, ~$$10^6$$ complex MACs per transform; per direction; per hop; two ways (FFT+iFFT) → tens of millions of ops/s at fine hops — doable on desktop, painful when stacked with a neural net on mobile, especially at 48 kHz with small hops.

### Cooley–Tukey radix-2 idea

If $$N=2^m$$, split even/odd indices:

$$
X[k]=E[k]+e^{-j2\pi k/N}O[k]
$$

$$
X[k+N/2]=E[k]-e^{-j2\pi k/N}O[k]
$$

where $$E$$ and $$O$$ are length-$$N/2$$ DFTs of even/odd parts. Recurse. The cost satisfies

$$
T(N)=2T(N/2)+\Theta(N).
$$

Unroll it: $$T(N)=\Theta(N)+2\Theta(N/2)+4\Theta(N/4)+\cdots$$, and there are $$\log_2 N$$ generations until the problem size is 1. Each generation sums to $$\Theta(N)$$, so $$T(N)=\Theta(N\log N)$$. Depth $$\log_2 N$$ stages, each stage $$\Theta(N)$$ work. For $$N=1024$$, $$\log_2 N=10$$ and the leading-term ratio $$N^2/(N\log_2 N)=1024/10=102.4$$. That is about a hundred times fewer multiply-adds before you count that a real PCM FFT can skip the redundant half. It is not a claim that wall-clock time drops by exactly 102; constants, SIMD, and Python overhead move the measured ratio, which is what the mini-lab is for.

The twiddle $$e^{-j2\pi k/N}$$ is the “butterfly” rotation. In-place implementations overwrite buffers; **bit-reversed** order appears in some stages — libraries hide this, but debugging raw implementations needs awareness.

### Short video: why FFT is fast

A short reel from MathDiagram that asks how the FFT computes the Fourier transform so efficiently. Watch it after the even/odd split above.

<div class="video-embed" style="text-align:center;margin:1em 0;"><iframe src="https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Freel%2F4039621483008687&show_text=false&width=315&height=560" width="315" height="560" style="border:none;overflow:hidden;max-width:100%;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe></div>

If the video does not load, [open it on Facebook](https://www.facebook.com/reel/4039621483008687).

### Complexity comparison (order of magnitude)

| $$N$$ | $$N^2$$ | $$N\log_2 N$$ |
|------:|--------:|--------------:|
| 256 | 65k | ~2k |
| 512 | 262k | ~4.5k |
| 1024 | 1.0M | ~10k |

Constants matter (complex vs real, SIMD), but the scaling is why FFT is mandatory.

### Real-input FFT

Speech PCM is real. A real-FFT computes packed Hermitian spectrum with roughly half the work of a full complex FFT. Use it when APIs allow. Neural graphs sometimes consume complex or magnitude features — still compute efficiently underneath.

### Non-power-of-two

DeepFilterNet-style windows may use sizes like 960 samples (20 ms at the 48 kHz full-band rate used by `deepfilternet3-noise-filter`). Note that $$960=2^6\cdot 3\cdot 5$$, so a mixed-radix FFT applies directly; you do not need a power of two for the transform to exist. FFTs of that length are fine (mixed radix, Bluestein’s chirp z-transform, or pad to 1024). Padding to 1024 is simple but changes bin centers slightly and costs a bit more — document what training used. Running a length-256 plan because “FFT means power of two” on 48 kHz frames is a different bug: you have changed $$N$$, not sped up the same DFT.

### Plans and allocations

Production rules:

1. **Create FFT plans once** (FFTW wisdom, pocketfft setup, Rust realfft plans, etc.).
2. **Never allocate** on the audio thread.
3. Prefer **SIMD** builds (WASM SIMD, NEON, AVX) when packaging (Ch. 06).
4. In **ONNX Runtime**, STFT may be a graph op or a pre-process outside the graph — know which, for profiling.

### When FFT dominates vs neural ops

Tiny classical NS: FFT+iFFT may dominate. DeepFilterNet-class nets: neural matmuls usually dominate, but FFT is still non-negligible at high rates / small hops / debug builds without SIMD. Profile both.

## Worked examples

### Hand-checking a 4-point butterfly on $$x = [1, 0, -1, 0]$$

Split $$x$$ into even indices $$x_{\text{even}} = [1, -1]$$ and odd indices $$x_{\text{odd}} = [0, 0]$$:
- Length-2 DFT of even part: $$E[0] = 1 + (-1) = 0$$, $$E[1] = 1 - (-1) = 2$$.
- Length-2 DFT of odd part: $$O[0] = 0$$, $$O[1] = 0$$.
- Combine with twiddle $$W_4^k = (-j)^k$$:
  - $$k = 0$$: $$X[0] = E[0] + 1\cdot O[0] = 0$$, $$X[2] = E[0] - 1\cdot O[0] = 0$$.
  - $$k = 1$$: $$X[1] = E[1] + (-j)\cdot O[1] = 2$$, $$X[3] = E[1] - (-j)\cdot O[1] = 2$$.

Result $$[0, 2, 0, 2]$$ matches the full $$4\times 4$$ matrix product from Lesson 01-04—using only half-size sub-DFTs!

### Ops budget sketch

Hop 10 ms → 100 FFT+iFFT pairs/s/channel. $$N=512$$ complex FFT ~ $$5\cdot10^3$$ MACs order → $$10^6$$ MACs/s for FFT side — small vs a multi-layer conv-RNN. At hop 2.5 ms and $$N=1024$$ without real-FFT, costs rise fast.

### Pad 960→1024

20 ms @ 48 kHz = 960. Pad 64 zeros: denser DTFT sampling, slightly different from training if training used exact 960 mixed-radix — **match training**.

---

### Deep-Dive Explanation: How One Algebraic Sign Flip Saves 100× the Work (Read Slowly)

#### Step 1: Split the DFT sum into even and odd time indices
Write $$n = 2m$$ for even indices and $$n = 2m + 1$$ for odd indices:
$$
X[k] = \sum_{m=0}^{N/2-1} x[2m] e^{-j2\pi k(2m)/N} + e^{-j2\pi k/N}\sum_{m=0}^{N/2-1} x[2m+1] e^{-j2\pi k(2m)/N} = E[k] + W_N^k O[k].
$$

#### Step 2: Exploit half-period symmetry to get two outputs for the price of one
Notice that $$E[k]$$ and $$O[k]$$ are periodic with period $$N/2$$, while the twiddle flips sign half a circle later: $$W_N^{k + N/2} = e^{-j\pi} W_N^k = -W_N^k$$! Therefore you compute $$W_N^k O[k]$$ **once**, add it to $$E[k]$$ to get $$X[k]$$, and subtract it from $$E[k]$$ to get $$X[k + N/2]$$ for free!

#### Step 3: Recurse $$\log_2 N$$ levels deep
Each split cuts problem size in half while keeping total work per level at $$O(N)$$. For $$N = 1024$$, there are only $$\log_2 1024 = 10$$ levels—shrinking $$1{,}048{,}576$$ ops to $$\approx 10{,}240$$!

Summary of the Cooley–Tukey speedup:

$$
\text{DFT } O(N^2)
\;\xrightarrow{\text{Even/Odd split}}\;
E[k] \pm W_N^k O[k]
\;\xrightarrow{\log_2 N \text{ stages}}\;
\text{FFT } O(N\log N)\ (\sim 100\times \text{ faster at } N=1024).
$$

## Common pitfalls

1. Rebuilding FFT plans every hop.
2. Using complex FFT APIs on real data without packing gains.
3. Assuming $$O(N\log N)$$ means “free.”
4. Changing $$N$$ to next power of two without verifying model compatibility.
5. Comparing timings from DEBUG vs Release / without SIMD.

## Mini-lab

**Goal.** Time a direct DFT matrix-vector product against `numpy.fft.fft` at $$N=256$$ and $$N=1024$$. This is an order-of-magnitude check, not a benchmark paper.

```python
import time
import numpy as np

def naive_dft(x):
    n = np.arange(x.shape[0])
    X = np.empty(x.shape[0], dtype=np.complex128)
    for k in range(x.shape[0]):
        X[k] = np.dot(x, np.exp(-2j * np.pi * k * n / x.shape[0]))
    return X

rng = np.random.default_rng(1)
for N in (256, 1024):
    x = rng.standard_normal(N)
    t0 = time.perf_counter()
    Xn = naive_dft(x)
    t_naive = time.perf_counter() - t0
    t0 = time.perf_counter()
    Xf = np.fft.fft(x)
    t_fft = time.perf_counter() - t0
    err = np.max(np.abs(Xn - Xf))
    print(N, f"naive_s={t_naive:.4f}", f"fft_s={t_fft:.6f}", f"err={err:.2e}")
```

**Expected.** `err` below `1e-8` at both sizes (around `1e-12` and `1e-11` on a typical laptop). Naive time at $$N=1024$$ is several times the naive time at $$N=256$$, on the order of the $$4^2=16$$ growth of $$N^2$$, with loop overhead eating part of that factor. FFT time stays well under 1 ms. At $$N=1024$$ the naive call is hundreds of times slower than `np.fft.fft`. Absolute seconds will not match a classmate’s machine.

**Failure modes.** Treating one timing run as a published RTF. Forgetting that this “naive” loop still uses a vectorized `np.dot` per bin, so it is not a pure Python double loop. Comparing a warm FFT to a first-call naive that also builds twiddles, then quoting the ratio as the Cooley–Tukey constant.

## Mini exercises

1. Compute $$\log_2 1024$$ stages; rough $$N\log N$$ vs $$N^2$$.
2. Why does real-FFT roughly halve work?
3. List three FFT implementation concerns on AudioWorklet/WASM.
4. If hop halves and $$N$$ fixed, how does FFT CPU roughly scale?
5. Give one reason to avoid padding when using pretrained STFT front-ends.

### Answer hints

1. $$\log_2 1024=10$$ stages. $$N\log_2 N=10240$$ against $$N^2=1048576$$, a factor of about 102 in the leading term.
2. Real spectra are conjugate symmetric, so a packed algorithm skips the redundant half of the bins. The savings are about half, not a second asymptotic class.
3. No allocations on the audio thread, reuse the FFT plan, and ship a SIMD build. A fourth you should also name: do not rebuild twiddle tables per hop.
4. Hops per second double, so FFT work per second roughly doubles if $$N$$ stays fixed.
5. Padding moves bin centers and the length the weights saw. A pretrained front-end then reads the wrong Hertz for the same index.

## Further reading

- Cooley & Tukey FFT lineage overviews (classic DSP references; Oppenheim & Schafer FFT sections).
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — FFT factorization as a faster DFT, not a different transform.
- ONNX STFT / DFT operator docs when using ORT graphs.

## Video tham khảo

- [The Fast Fourier Transform (FFT)](https://www.youtube.com/watch?v=E8HeD-MUrjY) — Steve Brunton, English. **xem trước.** Watch the contrast between the dense DFT and the factored FFT; the lesson's O(N log N) claim is this argument.
- [The Fast Fourier Transform Algorithm](https://www.youtube.com/watch?v=toj_IoCQE-4) — Steve Brunton, English. The radix-2 split is the part to watch: half-size transforms and twiddle factors, which is where the log factor comes from.
- [Computing the DFT Matrix](https://www.youtube.com/watch?v=Xw4voABxU5c) — Steve Brunton, English. Keep this as the O(N²) baseline the FFT is not allowed to change numerically.
