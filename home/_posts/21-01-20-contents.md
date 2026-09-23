---
layout: post
title: contents
chapter: home
order: 1
owner: Nguyen Le Linh
---

Real-time audio noise suppression for Vietnamese software engineers: **deep Fourier & audio DSP**, through DeepFilterNet and Mezon product integration.

# Course objectives

- Build strong Fourier / DFT / FFT intuition and a full framed-audio pipeline (STFT/ISTFT, windows, OLA).
- Connect classical NS / AEC / beamforming front-ends to modern neural SE.
- Understand the DeepFilterNet family and when ultra-light streaming models fit.
- Ship constraints: RTF, AudioWorklet, on-device ORT/tract/WASM, WebRTC / LiveKit.
- Evaluate with SI-SDR, DNSMOS, listening tests, DNS Challenge-style suites.
- Capstone: techniques behind `mezonai/mezon-noise-suppression` (`deepfilternet3-noise-filter`).

## Course outline

### Chapter 00 — Introduction & problem framing
Noise types, realtime vs offline, course map, Mezon context.

### Chapter 01 — Fourier & discrete transforms (deep)
Continuous FT intuition → sampling, aliasing, Nyquist → DTFT / DFS / DFT → DFT as basis → FFT (radix-2, complexity) → FFT in realtime frames → engineer pitfalls checklist.

### Chapter 02 — Audio processing pipeline
PCM & rates → frames / hop / OLA → windowing & leakage → STFT/ISTFT for speech (DeepFilterNet tie-in) → time vs frequency filtering → reading spectrograms → pipeline latency–quality tradeoffs.

### Chapter 03 — Classical NS / AEC / beamforming
Spectral subtraction, Wiener, Kalman intuition, WebRTC APM, GSC/IVA as front-ends.

### Chapter 04 — Neural SE & DeepFilterNet family
Complex spectrograms, deep filtering; survey pointers to successors and ultra-light streaming models; RNNoise bridge.

### Chapter 05 — Real-time constraints
RTF, AudioWorklet / callbacks, ring buffers, underruns, streaming state.

### Chapter 06 — On-device inference
ONNX / tract / ORT, quantization, SIMD/WASM, packaging.

### Chapter 07 — Product integration
WebRTC / LiveKit TrackProcessor, CDN model loading, Mezon npm surface.

### Chapter 08 — Evaluation
SI-SDR, DNSMOS, listening tests, DNS Challenge-style metrics.

### Chapter 09 — Capstone
Mezon NS architecture, techniques beyond the wrapper, optional Rust `df-core`, project brief.

### Chapter 10 — References & further paths
Curated reading list and maintenance notes.

## Primary references (starter)

- DeepFilterNet / DeepFilterNet2 / DeepFilterNet3 papers and official code.
- DNS Challenge (datasets, DNSMOS, baselines).
- WebRTC APM, SpeexDSP, RNNoise.
- SI-SDR literature; ONNX Runtime / tract docs.
- Standard DSP references for FT / DFT / FFT / STFT.
