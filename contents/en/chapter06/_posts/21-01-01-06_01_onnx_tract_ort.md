---
layout: post
title: "06-01 ONNX, tract, and ORT"
chapter: "06"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter06
lesson_type: required
draft: false
---

On-device NS almost always **exports** a trained graph to an inference runtime. **ONNX** is the interchange format; **ONNX Runtime (ORT)** is the dominant cross-platform engine (including Web/WASM builds); **tract** is a Rust-native inference crate popular when you want a pure-Rust path. This lesson compares them at selection level, covers opset / dynamic-axes pitfalls, and explains why Mezon-style products often standardize on ORT/WASM.

## Learning objectives

You will explain ONNX as an SE interchange format, compare ORT vs tract for ecosystem and targets, list export pitfalls from PyTorch-style training, and sketch a streaming I/O contract with dynamic axes and RNN state.

## 60-minute teaching plan

- **0–10 min** — Why not ship PyTorch in AudioWorklet.
- **10–25 min** — ONNX graph concepts: nodes, initializers, opsets.
- **25–40 min** — ORT vs tract selection matrix.
- **40–50 min** — Export pitfalls; streaming axes.
- **50–60 min** — Pitfalls, exercises, Mezon default rationale.

## Core explanation

### ONNX in one paragraph

ONNX serializes a computation graph: tensors in/out, operators (`Conv`, `GRU`, `MatMul`, …), and weights as initializers. Training frameworks export; runtimes optimize and execute. For SE, the graph includes feature transforms *or* assumes you run STFT outside (common)—**know which side owns STFT**.

### Opset compatibility

Operators are versioned by **opset**. An export with opset 17 may not load on an older ORT. Pin:

- training export opset,
- ORT version in product,
- a CI test that loads the exact `.onnx` on the shipping runtime.

### ORT vs tract (selection level)

| Criterion | ONNX Runtime | tract |
|-----------|--------------|-------|
| Languages | C/C++, Python, Java, C#, JS/WASM, … | Rust-first |
| Web story | Strong (`onnxruntime-web`) | Not the primary web path |
| Optimizations | Graph opts, EP (CPU, CUDA, …) | Rust graphs, pulse/offline friendly |
| Product fit | Mezon web/native via ORT common | Attractive for Rust-native `df-core` experiments |
| Ops coverage | Broad, industry default | Check SE ops / custom layers |

**Rule of thumb:** choose ORT when you need WASM + wide platform parity; choose tract when building a Rust-native binary and the graph is supported—always verify operators on a real DF export.

### Dynamic axes for streaming

A streaming model may declare:

- `input_frame`: shape `[batch, features]` or `[batch, time, freq, 2]` with `time=1`,
- `state_in` / `state_out`: fixed hidden sizes,
- dynamic `batch` for parallelism (usually 1 in callbacks).

Export with explicit dynamic axes; test **batch=1 time=1** rigorously. Some exports accidentally bake `time=100` for offline chunks—unusable in callbacks.

### Export pitfalls from training frameworks

1. **Unsupported ops** (custom deep-filter layers)—need fusion to ONNX-friendly ops or custom ORT ops.
2. **In-place / control-flow** tracing mismatches (TorchScript/ONNX exporter issues).
3. **Missing state I/O** for GRUs—model looks stateless.
4. **Float64 leftovers** — force float32.
5. **Preprocessing drift** — numpy STFT in training vs Rust STFT in prod.

### Why Mezon paths often standardize on ORT/WASM

Browser delivery wants one artifact family; ORT Web provides a known performance playbook (SIMD, threads where allowed). Native can share the same ONNX file. Tract remains a valuable **optional Rust** path (Chapter 09 stretch) when embedding in a pure-Rust audio engine without JS.

## Checklist before freezing a model artifact

1. Loads on shipping ORT version.
2. Streams with state feedback matching training.
3. Bitwise or SNR-close to Python reference on a golden clip.
4. RTF_p95 within budget (05-01).
5. License of weights + third-party ops cleared.

## Pitfalls

- Shipping different ONNX files per OS without CI.
- Enabling CUDA EP in a product that must run on CPU-only laptops.
- Assuming tract supports every ORT model.
- Measuring RTF in Python ORT and expecting identical WASM numbers.

## Exercises

1. **I/O contract.** Write a table of tensor names/shapes for a toy GRU SE hop.
2. **Opset pin.** Given ORT version X, look up supported opset; pick an export opset (docs exercise).
3. **Compare.** 150-word memo: ORT vs tract for (a) Chrome extension (b) Rust CLI enhancer.
4. **Golden test.** Design a CI step: run ONNX vs PyTorch reference, fail if SI-SDR delta > threshold.

## Further reading

- ONNX and ONNX Runtime official documentation.
- `onnxruntime-web` docs (WASM).
- tract documentation (Rust-native inference).
- DeepFilterNet export discussions / community ONNX exports (verify before relying).
