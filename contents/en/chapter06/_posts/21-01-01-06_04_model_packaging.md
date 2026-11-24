---
layout: post
title: "06-04 Packaging models for products"
chapter: "06"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter06
lesson_type: required
draft: false
---

A correct ONNX graph still fails in a product when **packaging** is wrong: a huge first load, an uncached URL, a WASM file and a model archive from different generations, or a license you cannot hand to a customer. `deepfilternet3-noise-filter` **1.3.0** splits that problem. The npm package ships the JavaScript glue, the inlined AudioWorklet, and the loader. The heavy bytes, `df_bg.wasm` and `DeepFilterNet3_onnx.tar.gz`, are fetched from a CDN base you pass as `assetConfig.cdnUrl`. This lesson designs the layout, the version prefix rule, integrity, and the rollback path. Lesson 07-03 computes the full URLs.

![Packaged WASM and ONNX archive on the CDN side of the browser path]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. Packaging decides which bytes the WASM compile in the browser is allowed to see.*

A model file named `final_v3_fixed.onnx` sitting in a Slack thread is not a product artifact—it is an incident waiting to happen. The moment you ship real-time speech enhancement to millions of browser tabs or mobile installs, **packaging** becomes as important as model architecture: How fast does the bundle download on 4G? How do you guarantee the client loaded the exact weights matching the DSP front-end’s hop size and FFT window? And how do you roll back a bad release in 60 seconds without breaking cached clients?

This lecture turns raw `.onnx` and `.wasm` binaries into disciplined, versioned product artifacts with explicit **manifests**, **SHA-256 integrity checks**, **compression**, and **rollback safety**.

---

## Background Knowledge Map: Four Engineering Pillars of ML Artifact Packaging

Shipping ML weights reliably to edge devices requires four software-supply-chain practices:

1. **Co-Versioning Model + DSP Contract:** A speech model’s weights are meaningless without its exact preprocessing parameters (`sample_rate`, `n_fft`, `hop_size`, `window_type`, `norm_stats`). Bundling a JSON manifest alongside the weights prevents silent train/serve skew.
2. **Transport Compression (Brotli / Gzip) vs. Quantization:** Random-looking `FP32` mantissa bits barely compress under Gzip, whereas `INT8` weights compress well—pairing INT8 quantization with Brotli cuts transfer size by **5–6×**!
3. **Content-Addressed Integrity (SHA-256):** Naming artifacts by content hash (e.g., `ns-v2.1-9f3a8c.onnx`) eliminates stale-cache mismatches and lets clients verify integrity before instantiating the inference session.
4. **Lazy Loading & Feature-Tiered Bundles:** Ship a tiny JS/TS bootstrap (~15 KB) in the main app bundle, and fetch the heavy WASM + model weights asynchronously only when the user actually joins an audio call.

---

## Learning objectives

You will separate the npm tarball from the CDN artifacts, apply the path rule for package ≤ 1.1.2 versus ≥ 1.2.0 (including 1.3.0, which still auto-prefixes `v2/`), refuse a `cdnUrl` that already contains `v2`, and list the license and cache checks that belong in a ship gate.

## 60-minute teaching plan

- **0–10 min** — A first-run download that blocks the call, and why npm size is the wrong number.
- **10–25 min** — Artifact pair, suggested config, semver.
- **25–40 min** — Prefix rule, compression, immutable cache.
- **40–50 min** — Integrity, licenses, staged rollout.
- **50–60 min** — Mini-lab, pitfalls, exercises.

## Core explanation

### Two packages, one product

`npm install deepfilternet3-noise-filter` installs a library whose peer dependency is `livekit-client` ^2. The README states that worker and worklet sources are inlined as blob URLs, so Webpack, Vite, Rollup, esbuild, and Parcel do not need a copy plugin. That is the small, versioned JavaScript surface. It is not the model. `DeepFilterNet3Core.initialize()` fetches two bodies in parallel: the WASM module and the model archive. Those bodies dominate cold-start time. Quantization (lesson 06-02) and the SIMD build (lesson 06-03) change their size and their speed, but only after you publish the pair to a URL the client will actually request.

### Suggested sidecar, not a private API

A product mirror should carry enough metadata that a wrapper cannot drift silently. A teaching layout, which you own, looks like this:

```text
models/df3-mono-48k/
  df_bg.wasm
  DeepFilterNet3_onnx.tar.gz
  config.json             # hop, sample_rate, state shapes
  LICENSE_WEIGHTS.txt
  SHA256SUMS
  CHANGELOG.md
```

`config.json` is your manifest: sample rate (48000 for this package), hop, input names, and state shapes. The npm public API does not require you to upload a file with that name. The client requests exactly two paths under `cdnUrl`. Keep the manifest beside them for humans and for CI.

### README path rule

The package README specifies:

| Package | WASM | Model archive |
|---------|------|----------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm` | `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| ≥ 1.2.0, including 1.3.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` | `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |

The client adds `v2/` itself for ≥ 1.2.0. Do not put `v2` inside `cdnUrl`. A base that already ends in `/v2` becomes `.../v2/v2/...` and 404s. The example base in the package README is `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. The archive name is `DeepFilterNet3_onnx.tar.gz`, from the upstream Rikorose DeepFilterNet repository. The WASM file name is `df_bg.wasm`.

### Cache, compression, integrity

Serve the pair with Brotli or gzip. ONNX archives often compress well; WASM less so, but it still benefits. Prefer immutable, content-addressed names or an immutable version directory, with `Cache-Control: public, max-age=31536000, immutable`. Publish SHA-256 sums and verify after download in CI. Refuse to start a canary if the WASM hash and the model hash are not from the same release. A new SIMD module with last month’s archive is a packaging bug, not a model-quality bug.

Overwrite-in-place of a URL you told caches to keep for a year is how you poison clients. Roll forward by publishing a new directory. Keep the previous directory up so you can point `cdnUrl` back, or ship a package downgrade, without rebuilding the world. The JavaScript package version and the asset directory version move together in your compatibility matrix: opset, tract or ORT build, SIMD feature set, browser floor.

### Size is a channel decision

Teaching budgets, not measurements of this archive: a mobile web first load wants a small compressed pair, desktop can lazy-load a larger one, and a native app has store limits of its own. INT8 weights and ultra-light models (lesson 04-05) are how you hit the mobile number. They are chosen before the CDN upload, which is why the figure puts quantization on the left of the WASM compile.

### Legal packaging

The npm package is dual-licensed Apache-2.0 OR MIT, following upstream DeepFilterNet. Weights you redistribute need the same reading of the upstream license, plus third-party notices for the runtime. Do not put customer audio in the artifact. A model file is not a recording, but telemetry that stores voice metrics can be personal data. The optional instructor tree `/Users/nguyenlelinh/ncc/mezon-noise-suppression` is a local checkout for the teacher. Course work does not modify it.

### Staged rollout

Canary a small desktop cohort, watch underruns and init failures, then expand. Cold-start failures are packaging failures: 404, CORS, wrong MIME, double prefix. Steady-state underruns are real-time factor failures. Log them separately.

## Mini-lab

Run `python3 prefix_check.py`. The function encodes the README rule: a 1.3.0 `cdnUrl` must not already end with `/v2`.

```python
def prefix_ok(url):
    if url.rstrip("/").endswith("/v2"):
        return "double-prefix risk"
    return "base-ok"

print(prefix_ok("https://example.com/df3"))
print(prefix_ok("https://example.com/df3/v2"))
```

**Expected**

```text
base-ok
double-prefix risk
```

**Failure modes**

- Putting `v2` in `cdnUrl` because the README table shows `v2` in the resolved path. The prefix is the client’s job.
- Uploading only `df_bg.wasm` under `v2/pkg/` and leaving the tar.gz at the 1.1.2 path. The pair must match the package generation.
- Putting `v2` inside `cdnUrl` and also letting ≥ 1.2.0 add it, so the request 404s on `.../v2/v2/...`.
- Hashing the files on a laptop and publishing different bytes to the CDN.

## Pitfalls

- Judging the product by the npm install size.
- No manifest, so a hop change ships “successfully” and breaks overlap-add.
- Shipping a debug WASM.
- Query-string cache busters on every page load (`?t=Date.now()`), which defeat the CDN.
- Mixing ≤ 1.1.2 clients and ≥ 1.2.0 clients in one folder without both layouts present.

---

### Worked Numerical Example: Calculating Cold-Start Download Time on a 10 Mbps Mobile Link

Suppose a 1.2M-parameter streaming denoiser is packaged three ways and downloaded over a realistic **10 Mbps** ($$1.25	ext{ MB/s}$$) mobile connection:

| Artifact Variant | Raw Size | Brotli Wire Size | Download Time @ 10 Mbps | Fits Call-Join Budget (< 1 s)? |
| :--- | :--- | :--- | :--- | :--- |
| **FP32 ONNX (uncompressed)** | $$4.80	ext{ MB}$$ | $$4.35	ext{ MB}$$ | $$3.48	ext{ s}$$ | **No** (delays call join!) |
| **FP16 ONNX + Brotli** | $$2.40	ext{ MB}$$ | $$2.05	ext{ MB}$$ | $$1.64	ext{ s}$$ | Marginal |
| **INT8 ONNX + Brotli** | $$1.20	ext{ MB}$$ | $$0.85	ext{ MB}$$ | **$$0.68	ext{ s}$$** | **Yes!** |

Add a `0.45 MB` Brotli-compressed WASM SIMD runtime, and the entire INT8 package downloads in $$(0.85 + 0.45) / 1.25 = \mathbf{1.04	ext{ s}}$$ on first visit—and **0 ms network wait** on every subsequent call once cached!

### Deep-Dive Explanation: Four Rules for Bulletproof Model Packaging (Read Slowly)

1. **Never overwrite a live model URL in place:** Always publish immutable versioned URLs (`v2.1.0/...`) so an in-flight call never downloads half of v2.0 and half of v2.1.
2. **Validate the manifest schema before calling `InferenceSession.create`:** Verify `sample_rate`, `hop_size`, and `sha256` at load time so corrupted downloads fall back cleanly to passthrough audio instead of crashing the call.
3. **Separate runtime upgrades from weight upgrades:** Keeping the WASM engine and the `.onnx` weight blob independently versioned lets ML engineers ship improved weights without rebuilding the C++/Rust runtime.
4. **Budget for both download *and* WASM compilation/warmup:** Calling `WebAssembly.instantiateStreaming` overlaps network download with compilation, shaving hundreds of milliseconds off startup.

**Quick check.** Why do `FP32` neural network weight files compress poorly under Gzip/Brotli compared to text or JSON, and why does `INT8` quantization shrink the wire transfer so dramatically?

---

## Exercises

1. Write the fields your `config.json` must contain so a 48 kHz DeepFilter hop cannot drift.
2. Propose compressed-size budgets for mobile web and desktop, and state which knob (INT8, ultra-light model, lazy load) hits each budget.
3. Document a rollback that restores the previous artifact pair without editing the product repository.
4. List the license questions you must answer before redistributing `DeepFilterNet3_onnx.tar.gz` commercially.
5. A teammate sets `cdnUrl` to `https://cdn.example.com/df3/v2`. What URLs will a ≥ 1.2.0 client request if it follows the README and prefixes `v2` again?

### Answer hints

1. Sample rate, hop, window, model input names, state shapes, and the package version the shapes were checked against.
2. Mobile: quantize or swap in a smaller model and keep the pair on the CDN, not inside npm. Desktop: lazy-load is acceptable if join is not blocked (lesson 07-02).
3. Keep the previous directory. Point `cdnUrl` at the base that resolves to it, or pin the older package. Do not overwrite immutable URLs.
4. Upstream license, the package’s Apache-2.0 OR MIT dual license, trademark, and whether your mirror may rehost the archive. Read the upstream model card. Do not guess “non-commercial” without the text.
5. `https://cdn.example.com/df3/v2/v2/pkg/df_bg.wasm` and `.../v2/v2/models/DeepFilterNet3_onnx.tar.gz`. That is the double-prefix failure.

## Further reading

- Package README, Custom CDN Configuration: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- [ONNX Runtime documentation](https://onnxruntime.ai/docs/) on optimized model artifacts.
- Upstream archive [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Chapter 07 for LiveKit `TrackProcessor` loading and CDN failure policy.

## Video tham khảo

- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, English. **xem trước.** Watch the path from a trained graph to a smaller file a client can load. Packaging in the lesson is this file plus the WASM and the cache, not a new network.
- [What is a CDN (Content Delivery Network) and How does a CDN Work?](https://www.youtube.com/watch?v=rIAIzf6utOc) — Cloudflare, English. A CDN caches that file near the user. Watch cache versus origin; a model archive is just a large static asset.
- [Quantization explained with PyTorch - Post-Training Quantization, Quantization-Aware Training](https://www.youtube.com/watch?v=0VdNflU08yA) — Umar Jamil, English. Quantization is the size lever inside the package. Watch the accuracy cost before you celebrate the smaller download.
