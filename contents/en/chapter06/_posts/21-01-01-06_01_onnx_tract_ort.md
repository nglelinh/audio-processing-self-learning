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

On-device noise suppression almost always **exports** a trained graph to an inference runtime. **ONNX** is the interchange format; **ONNX Runtime (ORT)** is the dominant cross-platform engine, including Web builds; **tract** is the Rust-native crate used when you want a pure-Rust path. Package `deepfilternet3-noise-filter` **1.3.0** does not ship PyTorch to the browser. Its public release notes say the WASM path was rebuilt against **tract 0.23.3**. The browser then receives a compiled WASM module plus the upstream archive `DeepFilterNet3_onnx.tar.gz`, not a Python session. This lesson fixes the selection criteria, the streaming I/O contract, and the shape mistakes that make a graph load in a notebook and fail inside an AudioWorklet.

![ONNX graph exported to a WASM module the browser loads beside the model archive]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. ONNX is the interchange file; tract or ORT executes it; the browser ultimately instantiates WASM.*

Training a speech model in PyTorch is only half the journey—you cannot ship a 2-gigabyte PyTorch + Python installation inside a browser tab or a 5 MB mobile SDK! To cross from research notebook to production device, you export the computational graph to **ONNX (Open Neural Network Exchange)** and execute it with a dedicated inference engine—most commonly **ONNX Runtime (ORT)** in C++/WASM or **tract** in pure Rust.

This lecture compares ONNX, ORT, and `tract` through a systems-engineering lens: how static shapes unlock zero-allocation execution plans, why operator coverage (especially GRUs, FFTs, and custom ops) decides which runtime you can pick, and how binary size trades off against peak SIMD throughput.

---

## Background Knowledge Map: Graph IRs, Static Execution Plans, and Runtime Trade-Offs

Four systems principles guide your choice of inference runtime for real-time audio:

1. **ONNX as a Portable Static Graph IR:** Exporting with `torch.onnx.export` freezes Python control flow into a typed DAG of standard operators (`Conv`, `GRU`, `MatMul`, `Add`) plus serialized constant weights.
2. **Static Shapes Enable Pre-Allocated Memory Arenas:** For streaming audio, every frame has the *exact same shape* (e.g., `[1, 1, 257]`). Declaring fixed static shapes lets both ORT and `tract` compute an entire memory plan once at startup—achieving near-zero heap allocations inside the audio loop.
3. **ONNX Runtime (ORT) vs. `tract` (Pure Rust):**
   - **ORT:** Battle-tested C++ engine with rich hardware Execution Providers (CoreML, DirectML, NNAPI, WASM SIMD), wider op coverage, larger binary footprint (several MB).
   - **`tract`:** Pure Rust, tiny self-contained binary (ideal for Rust native apps and lean WASM bundles), deterministic static planning (`into_optimized().into_runnable()`), slightly narrower op set.
4. **Graph Fusion & Constant Folding:** Both runtimes fuse adjacent `Conv + BatchNorm + ReLU` or `MatMul + Add` nodes at load time, eliminating intermediate tensor writes to RAM.

---

## Learning objectives

You will explain ONNX as a speech-enhancement interchange format, compare ORT and tract for a browser product versus a Rust binary, list export pitfalls that show up only on a one-hop stream, and check whether a tensor shape is an image-style NCHW blob or a DeepFilter-style frame `[1, T, F]` before anyone calls a session.

## 60-minute teaching plan

- **0–10 min** — Why an AudioWorklet cannot host a training framework.
- **10–25 min** — Graph, initializers, opset, and who owns the STFT.
- **25–40 min** — ORT versus tract, including the 1.3.0 tract pin.
- **40–50 min** — Dynamic axes, state tensors, and the shape cartoon.
- **50–60 min** — Mini-lab, pitfalls, exercises.

## Core explanation

### What the file actually contains

An ONNX file is a computation graph: named tensors in and out, operators such as `Conv`, `GRU`, and `MatMul`, and weights stored as initializers. The training framework writes the file. A runtime optimizes and executes it. For speech enhancement the graph either contains the feature transform or assumes you run the STFT outside the session. DeepFilter-class models are usually the second kind: the runtime consumes a spectral frame, and your overlap-add lives beside it. If those two sides disagree on hop, window, or frequency count, the session can still return tensors while the audio sounds wrong.

### Opset and runtime pin

Operators are versioned by **opset**. An export at opset 17 may refuse to load on an older ORT build. Pin three things together: the export opset, the ORT or tract version in the product, and a CI job that loads the exact `.onnx` on the runtime you ship. The 1.3.0 release notes of `deepfilternet3-noise-filter` name tract **0.23.3** for the WASM build. That pin is a product fact from the changelog, not a reason to skip an operator check. Tract and ORT do not implement every op the same way. A graph that `onnxruntime` imports in Python can still fail in tract if a custom deep-filter layer was not fused into supported ops.

### ORT versus tract

| Criterion | ONNX Runtime | tract |
|-----------|--------------|-------|
| Languages | C/C++, Python, Java, C#, JS/WASM | Rust-first |
| Web story | `onnxruntime-web` | Not the primary browser path |
| Optimizations | Graph opts, execution providers | Rust graphs, streaming-friendly |
| Product fit | Wide platform parity | The Rust path behind the 1.3.0 WASM notes |
| Ops coverage | Broad default | Verify on a real DeepFilter export |

Choose ORT when you need one ONNX file checked from Python and a documented Web backend. Choose tract when the shipping binary is Rust and you have verified the operators. The Mezon package’s browser path is WASM built from the DeepFilter `libDF` stack, with tract called out in the 1.3.0 notes. Chapter 09’s optional `df-core` experiment is the place to link tract yourself. Do not treat the npm wrapper as a second model.

### Streaming axes

A streaming model should declare a frame whose time axis is one hop, plus recurrent state in and out. A typical teaching contract is `features` with shape `[1, T, F]` and `T = 1` in the callback, together with fixed-size `state_in` / `state_out`. Dynamic batch is useful for offline parallelism and almost always 1 inside the audio callback. Export those axes explicitly. Some exports bake `T = 100` from an offline validation script. That graph loads, then rejects every real-time hop.

NCHW layouts such as `[1, 3, 224, 224]` are image conventions. A rank-4 tensor is the wrong shape for a DeepFilter frame even when the numbers look “batched.” Rank 3 with a leading 1 is the cartoon this lesson accepts. The real next step, after the cartoon, is `ort.InferenceSession` and a check that the **input name** matches the graph, not only the rank.

### Export pitfalls

1. **Unsupported ops** in custom deep-filter layers. Fuse them to ONNX-friendly ops or register a custom runtime op. Do not invent a private op name and hope CI is kind.
2. **Control-flow and in-place** tracing mismatches between the training step and the exported graph.
3. **Missing state I/O** on GRUs, so the model looks stateless and pumps from hop to hop.
4. **Float64 leftovers.** Force float32 before you quantize or compile WASM.
5. **Preprocessing drift.** A NumPy STFT in training versus the WASM STFT in the product.

### Why the browser path standardizes on a compiled module

The package does not ask the page to construct an ORT session by hand. `DeepFilterNet3Core.initialize()` fetches the WASM bytes and the model archive, then `WebAssembly.compile`s the module on the main thread. `createAudioWorkletNode` runs only after that compile. Heavy work stays off the audio callback (Chapter 05). ORT remains the right tool for Python parity checks and for products that ship `onnxruntime-web` directly. Measure real-time factor on the WASM build you ship. A Python ORT timing is a different machine.

## Mini-lab

Optional, if ONNX Runtime is installed: `python3 -c "import onnxruntime"`. The required lab is the shape cartoon. Save it as `shape_check.py` and run `python3 shape_check.py`.

```python
def verdict(shape):
    rank = len(shape)
    if rank == 4:
        return "NCHW rejected-by-df-frame"
    if rank == 3 and shape[0] == 1:
        return "DF frame [1, T, F] accepted"
    return "rejected"

for shape in [(1, 3, 224, 224), (1, 1, 96), (96,)]:
    print(f"{list(shape)} -> {verdict(shape)}")
```

**Expected**

```text
[1, 3, 224, 224] -> NCHW rejected-by-df-frame
[1, 1, 96] -> DF frame [1, T, F] accepted
[96] -> rejected
```

**Failure modes**

- Treating “accepted” here as proof the real graph will run. The cartoon only checks rank and a leading batch of 1.
- `ort.InferenceSession` is the real next step. **Session input name mismatch** is the usual failure: the shape is right and the input is still named `input` in your code while the graph says `feat_erb` or similar. Read `session.get_inputs()`.
- A dynamic axis left at export-time `T = 100` passes a loose rank check and still rejects a hop of length 1.

## Pitfalls

- Shipping a different ONNX file per operating system without a load test.
- Enabling a CUDA execution provider in a product that must run on CPU-only laptops.
- Assuming tract supports every model ORT accepts.
- Copying Python ORT real-time factor numbers onto the WASM build.
- Calling `createAudioWorkletNode` before `initialize()` has compiled the module. The core throws if you do.

---

### Worked Numerical Example: Counting Tensor I/O Overhead vs. Compute on a 10 ms Frame

Suppose a streaming denoiser processes 10 ms frames (100 frames/s) with input `[1, 1, 257]` (`f32`), output `[1, 1, 257]` (`f32`), and state `[1, 128]` (`f32`):

1. **Raw I/O payload per frame:**
   $$(257 + 257 + 128 + 128)	ext{ floats} 	imes 4	ext{ bytes} = 770 	imes 4 = 3{,}080	ext{ bytes} pprox 3.0	ext{ KB/frame}.$$
   At 100 frames/s, that is only $$308	ext{ KB/s}$$ of tensor data—tiny!
2. **Runtime comparison for a 1.2 MB streaming model:**

| Dimension | ONNX Runtime (WASM / Native) | `tract` (Pure Rust) |
| :--- | :--- | :--- |
| **WASM / Binary Overhead** | ~3–8 MB (gzipped ~1–2.5 MB) | ~0.5–1.5 MB (lean Rust crate) |
| **Startup Plan Optimization** | Session graph optimization + arena alloc | `with_input_fact` $$	o$$ `into_optimized()` |
| **Per-Frame Allocation Risk** | Low with `IOBinding` / reused buffers | Zero-alloc possible with reusable `TVec` |
| **Best Fit** | Broad ops, GPU/NPU EPs, JS/TS teams | Pure Rust SDKs, tight WASM size budgets |

Notice the trap: even though the tensor payload is only 3 KB, if a JS wrapper allocates *new* `ort.Tensor` objects and copies buffers on every 10 ms frame, you trigger 100 heap allocations/sec—causing GC micro-stutters!

### Deep-Dive Explanation: Four Rules for Painless ONNX Export and Deployment (Read Slowly)

1. **Fix opset version and freeze static frame shapes:** Avoid dynamic sequence axes (`seq_len = "T"`) for streaming inference; locking `seq_len = 1` unlocks stronger operator fusion and simpler memory planning.
2. **Keep STFT/iSTFT outside the ONNX graph:** Complex FFT operators have uneven support across ORT/tract/WASM backends; run STFT/iSTFT in clean Rust/C++/WASM DSP code and pass real-valued magnitude/complex pairs into ONNX.
3. **Verify numerical parity immediately after export:** Compare PyTorch output vs. ORT/tract output on the same frame and assert $$\max\lvert y_{	ext{onnx}} - y_{	ext{torch}}
vert < 10^{-5}$$ before integrating into audio callbacks.
4. **Measure cold-start load time as well as per-frame RTF:** Downloading a 10 MB WASM runtime + compiling it on a slow mobile connection can delay call join by seconds.

**Quick check.** Why does exporting a streaming denoiser with static input shape `[1, 1, 257]` generally run faster and allocate less memory than exporting with dynamic shape `[batch, time, 257]`?

---

## Exercises

1. Write a tensor table for a toy GRU hop: names, ranks, and which tensors are state.
2. Given an ORT version, look up its supported opset in the [ONNX Runtime docs](https://onnxruntime.ai/docs/) and pick an export opset.
3. In about 150 words, choose ORT or tract for a Chrome extension and again for a Rust CLI enhancer.
4. Design a CI step that fails when ONNX and a PyTorch reference differ by more than a stated SI-SDR threshold on one golden clip.
5. Explain why `[1, 3, 224, 224]` must not be fed to a frame model even if batch size is 1.

### Answer hints

1. Include `frame` shaped `[1, 1, F]`, `state_in`, and `state_out` with equal hidden sizes. Mark the STFT as outside the session if the graph has no FFT op.
2. The export opset must be one the shipping runtime documents, not the newest opset your trainer offers.
3. Extension: a WASM runtime with a known browser matrix. CLI: tract if the ops check passes, because you avoid a second native library. Either answer needs the operator check.
4. Fix the clip, the hop, and the threshold in the job. Fail on missing state outputs as well as on SI-SDR.
5. Rank 4 is NCHW. The frame contract in the mini-lab is rank 3.

## Further reading

- [ONNX Runtime documentation](https://onnxruntime.ai/docs/), including quantization and Web topics used in the next lessons.
- [tract](https://github.com/sonos/tract), the Rust inference library named in the package’s 1.3.0 notes.
- npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter) and the [repository](https://github.com/mezonai/mezon-noise-suppression). Optional instructor checkout, not a course edit target: `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.
- DeepFilterNet export discussions. Verify any community ONNX file before you depend on it.

## Video tham khảo

- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, English. **xem trước.** Watch ONNX as the interchange file and ONNX Runtime as the engine that runs it on CPU, GPU, and the edge. Tract is the Rust engine in the lesson; this talk is the format and the dominant runtime.
- [Introduction to ONNX Runtime](https://www.youtube.com/watch?v=Wp5PaRpudlk) — NVIDIA Developer, English. A second official introduction to the same runtime, useful for the execution-provider picture the lesson needs before any WASM build.
