---
layout: post
title: "09-03 Optional Rust native (df-core) path"
chapter: "09"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter09
lesson_type: required
draft: false
---

The supported Mezon path is the WASM box in `deepfilternet3-noise-filter`: ONNX weights, a SIMD WASM build, the `v2/` CDN layout the package adds for ≥ 1.2.0 (including 1.3.0), and an AudioWorklet. A Rust crate you might call `df-core` is a **stretch alternative to that box**, for a desktop CLI or a native embed you build in your own workspace. It is not a second product, it is not required to pass, and it is not a folder you are entitled to find under `/Users/nguyenlelinh/ncc/mezon-noise-suppression`. If your first backend only copies samples from input to output, label it **passthrough**. Never write “NS works” on a passthrough build.

![On-device WASM path for deepfilternet3-noise-filter]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. The shipping path is PyTorch to ONNX to WASM to the package or CDN `v2/` assets, then AudioWorklet. Rust `df-core` is a stretch alternative to this WASM box, not a second product beside it.*

## What you should be able to do

You should be able to say what the WASM path loads (`df_bg.wasm`, `DeepFilterNet3_onnx.tar.gz`), what a personal Rust experiment would have to match (frame hop, sample rate, a real model), and how you will prove parity without claiming bit-exactness you have not measured. You should also refuse to treat a passthrough backend as enhancement.

## The box you are not replacing by default

Package 1.3.0, like every release ≥ 1.2.0, requests `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`. The client adds `v2/`. Do not put it in `cdnUrl`. The example base is `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. The public controls remain `DeepFilterNoiseFilterProcessor` or `DeepFilterNet3Core`, `setProcessor`, `setSuppressionLevel(0–100)`, and `setEnabled`. A Rust experiment does not get new public names in the npm package. If you want a CLI, you build it beside the course, in a personal repository.

The DeepFilterNet papers describe why a native reimplementation is picky: 48 kHz full-band audio, an STFT with a hop on the order of 10 ms, an ERB gain stage, and a deep filter that may use a short look-ahead. That look-ahead is algorithmic latency. Matching RTF is not the same as matching the waveform. Lesson 08-01 showed that a one-sample slip turns 13.80 dB into −10.67 dB. A Rust port that is “a little late” will look terrible on SI-SDR even when it sounds similar.

## A personal workspace, if you opt in

Create this only in your fork or a new repo. Do not add it to the shared product tree as the homework.

```text
my-df-stretch/
  df-core/     # your frame API
  df-cli/      # offline wav in, wav out
  README.md    # says passthrough or real backend, in the first paragraph
```

Suggested milestones, in order:

1. **Passthrough backend.** `process` returns the input samples. The README title says passthrough. Tests check length and a copy, not a noise floor.
2. **Asset errors.** A missing tar or ONNX path fails with a clear error. It does not silently pass audio and print “enhanced.”
3. **Load a real runtime.** [tract](https://github.com/sonos/tract) or ONNX Runtime ([onnxruntime.ai/docs](https://onnxruntime.ai/docs/)) runs the same DeepFilterNet3 archive the CDN serves. Upstream [libDF](https://github.com/Rikorose/DeepFilterNet) is the other honest option. Pick one and pin the version.
4. **Framing.** Document hop, window, and sample rate next to the WASM path. Do not invent a private Mezon API to do it.
5. **Golden files.** One noisy wav through the public WASM path, one through your CLI. Compare with SI-SDR **between the two estimates**, after alignment, and report the float. Also listen. High SI-SDR between them means they match each other, not that either matches clean speech.
6. **Stop conditions.** If you only finished step 1, the demo script says “passthrough, noise suppression is not running.”

Licensing follows the upstream DeepFilterNet project (Apache-2.0 OR MIT, as the npm package does). Do not commit the tar.gz. Point at the CDN layout or the upstream `models/` instructions.

## Parity without fiction

```text
align hop delay
enh_wasm.wav  from the published processor or an offline WASM run you script
enh_rust.wav  from your CLI
print SI-SDR(enh_wasm, enh_rust) after alignment
write the float in the report
if the backend is passthrough, skip this comparison and say why
```

Until step 3 exists, the golden test is **pending**. A passthrough file compared to a real enhancer will score badly. That bad score is the point. Do not loosen the tolerance until the number looks kind.

tract versus a hand-written binding to upstream libDF is a tradeoff you should write in a paragraph: tract and ONNX Runtime consume the ONNX artifact the CDN already ships; libDF is the engine the WASM build is derived from and may track streaming state more faithfully. Either way you still measure. Chapter 06 is the background. This lesson does not add a private symbol table.

## What “done” means for a stretch

Done for the optional path is a README a stranger can build, a passthrough label if that is all you have, or a CLI plus one SI-SDR float against the WASM output if you loaded a model. Done is not a slide that says the native client is production Mezon. The shipping client remains the npm package on the LiveKit path in 09-01.

## Mini-lab

Write `df_core_status.md` with two lines a checker can see:

```text
backend: passthrough
claim: noise suppression is not running
```

If you truly load a model, you may instead write `backend: tract` or `backend: onnxruntime` or `backend: libdf`, and `claim: compared to wasm SI-SDR <float>`. The passthrough wording must not appear next to a claim that NS works.

```python
from pathlib import Path
text = Path("df_core_status.md").read_text().lower()
ok_pass = "passthrough" in text and "not running" in text
ok_real = any(k in text for k in ("tract", "onnxruntime", "libdf")) and "si-sdr" in text
bad = "ns works" in text or "noise suppression works" in text
print("status", "ok" if (ok_pass or ok_real) and not bad else "fix")
```

Expected output for the default stretch lab (no model yet):

```text
status ok
```

Failure modes: “NS works” on a copy loop; committing `DeepFilterNet3_onnx.tar.gz`; requiring the instructor’s machine path; describing Rust as the product and WASM as the demo; a parity float with no alignment note.

## Exercises

1. Write five milestones you can finish without a GPU, marking which ones are passthrough.
2. List tests that do not need weights: frame length, identity copy, and a missing-file error.
3. In one paragraph, compare tract (or ONNX Runtime) with upstream libDF as the stretch backend.
4. Decide go or no-go for Rust in your capstone. Name the WASM work you will do if you say no-go.
5. State the SI-SDR comparison direction: estimate versus estimate, not estimate versus a slogan.

### Answer hints

1. Steps 1–2 are passthrough-legal. Step 3 is the first time the word enhancement is allowed.
2. Identity: output samples equal input samples. Missing file: non-zero exit status and no “enhanced” wav.
3. ONNX runtimes consume the tar/ONNX the CDN already has. libDF is the upstream engine. Both need a golden.
4. No-go is a complete capstone if 09-01 and 09-04 are real. Say so.
5. SI-SDR(wasm, rust) after delay compensation. The 13.80 lab is the method, not the expected product score.
