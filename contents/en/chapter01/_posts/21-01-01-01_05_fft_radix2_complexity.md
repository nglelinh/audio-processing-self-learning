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

Naive DFT is \(O(N^2)\). Real-time speech cannot afford that at every hop on a phone CPU or inside AudioWorklet. This lesson explains why FFT is \(O(N\log N)\), what radix-2 buys you, and which practical constraints show up in ORT/WASM/native stacks.

## Learning objectives

1. Explain why FFT is \(O(N\log N)\) versus naive \(O(N^2)\) DFT.
2. Describe radix-2 Cooley–Tukey divide-and-conquer at a cartoon level.
3. List practical constraints: power-of-two sizes, real-FFT optimizations, plan reuse.
4. Estimate FFT cost relative to neural ops in a hop budget.
5. Know what “calling FFT” means inside ONNX graphs vs hand-written WASM.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Complexity arithmetic: \(N=1024\) naive vs FFT ops order |
| 10–28 | Radix-2 butterfly idea; bit reversal awareness |
| 28–42 | Real FFT packing; non-power-of-two Bluestein/mixed radix (awareness) |
| 42–52 | Library landscape: native, WASM SIMD, ORT FFT ops |
| 52–60 | Exercises |

## Core explanations

### Naive cost

Each of \(N\) outputs sums \(N\) complex multiply-adds → \(\Theta(N^2)\). For \(N=1024\), ~\(10^6\) complex MACs per transform; per direction; per hop; two ways (FFT+iFFT) → tens of millions of ops/s at fine hops — doable on desktop, painful when stacked with a neural net on mobile, especially at 48 kHz with small hops.

### Cooley–Tukey radix-2 idea

If \(N=2^m\), split even/odd indices:

$$
X[k]=E[k]+e^{-j2\pi k/N}O[k]
$$

$$
X[k+N/2]=E[k]-e^{-j2\pi k/N}O[k]
$$

where \(E\) and \(O\) are length-\(N/2\) DFTs of even/odd parts. Recurse. Depth \(\log_2 N\) stages, each stage \(\Theta(N)\) work → \(\Theta(N\log N)\).

The twiddle \(e^{-j2\pi k/N}\) is the “butterfly” rotation. In-place implementations overwrite buffers; **bit-reversed** order appears in some stages — libraries hide this, but debugging raw implementations needs awareness.

### Complexity comparison (order of magnitude)

| \(N\) | \(N^2\) | \(N\log_2 N\) |
|------:|--------:|--------------:|
| 256 | 65k | ~2k |
| 512 | 262k | ~4.5k |
| 1024 | 1.0M | ~10k |

Constants matter (complex vs real, SIMD), but the scaling is why FFT is mandatory.

### Real-input FFT

Speech PCM is real. A real-FFT computes packed Hermitian spectrum with roughly half the work of a full complex FFT. Use it when APIs allow. Neural graphs sometimes consume complex or magnitude features — still compute efficiently underneath.

### Non-power-of-two

DeepFilterNet-style windows may use sizes like 960 samples (20 ms @ 48 kHz). FFTs still exist (mixed radix, Bluestein’s chirp z-transform, or pad to 1024). Padding to 1024 is simple but changes bin centers slightly and costs a bit more — document what training used.

### Plans and allocations

Production rules:

1. **Create FFT plans once** (FFTW wisdom, pocketfft setup, Rust realfft plans, etc.).
2. **Never allocate** on the audio thread.
3. Prefer **SIMD** builds (WASM SIMD, NEON, AVX) when packaging (Ch. 06).
4. In **ONNX Runtime**, STFT may be a graph op or a pre-process outside the graph — know which, for profiling.

### When FFT dominates vs neural ops

Tiny classical NS: FFT+iFFT may dominate. DeepFilterNet-class nets: neural matmuls usually dominate, but FFT is still non-negligible at high rates / small hops / debug builds without SIMD. Profile both.

## Worked examples

### Ops budget sketch

Hop 10 ms → 100 FFT+iFFT pairs/s/channel. \(N=512\) complex FFT ~ \(5\cdot10^3\) MACs order → \(10^6\) MACs/s for FFT side — small vs a multi-layer conv-RNN. At hop 2.5 ms and \(N=1024\) without real-FFT, costs rise fast.

### Pad 960→1024

20 ms @ 48 kHz = 960. Pad 64 zeros: denser DTFT sampling, slightly different from training if training used exact 960 mixed-radix — **match training**.

## Common pitfalls

1. Rebuilding FFT plans every hop.
2. Using complex FFT APIs on real data without packing gains.
3. Assuming \(O(N\log N)\) means “free.”
4. Changing \(N\) to next power of two without verifying model compatibility.
5. Comparing timings from DEBUG vs Release / without SIMD.

## Mini exercises

1. Compute \(\log_2 1024\) stages; rough \(N\log N\) vs \(N^2\).
2. Why does real-FFT roughly halve work?
3. List three FFT implementation concerns on AudioWorklet/WASM.
4. If hop halves and \(N\) fixed, how does FFT CPU roughly scale?
5. Give one reason to avoid padding when using pretrained STFT front-ends.

## Further reading

- Cooley & Tukey FFT lineage overviews (classic DSP references; Oppenheim & Schafer FFT sections).
- FFTW / pocketfft / platform FFT documentation.
- ONNX STFT / DFT operator docs when using ORT graphs.
