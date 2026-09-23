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

## Learning objectives

You will separate the npm tarball from the CDN artifacts, apply the README path rule for package ≤ 1.1.2 versus the README rule for ≥ 1.2.0 and the `v3/` paths installed 1.3.0 actually requests, refuse a `cdnUrl` that already contains a version prefix, and list the license and cache checks that belong in a ship gate.

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
| 1.2.x, as the README still states for every ≥ 1.2.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` | `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |
| installed 1.3.0 `getAssetUrls()` | `{cdnUrl}/v3/pkg/df_bg.wasm` | `{cdnUrl}/v3/models/DeepFilterNet3_onnx.tar.gz` |

The client adds `v2/` itself for ≥ 1.2.0. Do not put `v2` inside `cdnUrl`. A base that already ends in `/v2` becomes `.../v2/v2/...` and 404s. The 1.3.0 source of `AssetLoader.getAssetUrls()` on the public repository prefixes `v3/` instead of the `v2/` string the README still prints. Treat the table above as the README contract this course self-checks. Before you upload a production mirror, print the URLs from the installed package and publish that directory. Do not invent a third filename. The archive name in both layouts is `DeepFilterNet3_onnx.tar.gz`, from the upstream DeepFilterNet repository. The WASM file name is `df_bg.wasm`.

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
- Trusting the README `v2` string when the installed `getAssetUrls()` prints `v3`. The lab checks the “do not embed the prefix” rule; the directory name comes from the package you actually ship.
- Hashing the files on a laptop and publishing different bytes to the CDN.

## Pitfalls

- Judging the product by the npm install size.
- No manifest, so a hop change ships “successfully” and breaks overlap-add.
- Shipping a debug WASM.
- Query-string cache busters on every page load (`?t=Date.now()`), which defeat the CDN.
- Mixing ≤ 1.1.2 clients and ≥ 1.2.0 clients in one folder without both layouts present.

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
