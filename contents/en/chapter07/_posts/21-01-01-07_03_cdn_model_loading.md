---
layout: post
title: "07-03 CDN model loading"
chapter: "07"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter07
lesson_type: required
draft: false
---

DeepFilterNet3 in the browser needs a **WASM** module and a model archive, `DeepFilterNet3_onnx.tar.gz`. Shipping both only inside the npm tarball bloats install and couples asset updates to application deploys. Production pages load them from a **CDN** (content delivery network): a cache in front of those two files. `deepfilternet3-noise-filter` **1.3.0** resolves the URLs from `assetConfig.cdnUrl`. This lesson makes the four URLs for 1.1.2 and 1.3.0 self-checking, and keeps a failed fetch from taking down the call.

![CDN fetch of WASM and the ONNX archive before AudioWorklet compile]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. The client turns cdnUrl into a WASM URL and a model URL, then compiles WASM.*

## Learning objectives

You will write the resolved URLs for package ≤ 1.1.2 and for the 1.3.0 README rule, keep `v2` out of `cdnUrl`, set cache headers that survive a version bump, and bypass suppression when the fetch fails.

## 60-minute teaching plan

- **0–10 min** — Which two bodies move, and when `initialize()` fetches them.
- **10–25 min** — `cdnUrl` and the version prefix.
- **25–40 min** — Cache, MIME, CORS.
- **40–50 min** — Readiness without blocking `connect()`.
- **50–60 min** — Mini-lab: four URLs.

## Assets

From the package README:

| Asset | Role |
|-------|------|
| `pkg/df_bg.wasm` under the base or under `v2/` | SIMD WASM glue for versions that enable it |
| `models/DeepFilterNet3_onnx.tar.gz` | Upstream DeepFilterNet3 archive |

Upstream pointer: [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz). The CDN serves **weights and code**, not user audio. Inference stays on device. Do not add an upload of PCM “for debugging” on a production client.

## Configuring the base

```javascript
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl: "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3"
  }
});
```

If you omit `cdnUrl`, the package default is that same Mezon base. A private mirror replaces the origin and the path prefix only.

### Version-specific paths

The README states:

| Package | Resolved paths |
|---------|----------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm` and `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| ≥ 1.2.0, including 1.3.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |

The package adds `v2/`. You do not. The README also says the SIMD build is about 20–30% faster for ≥ 1.2.0; cite that as the README’s number. Browsers for that build, again from the README: Chrome 91+, Firefox 89+, Safari 16.4+.

Package ≥ 1.2.0, including 1.3.0, adds `v2/` itself. You do not. Never put `v2` inside `cdnUrl`. The public example base is `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. The 1.3.0 changelog also records a tract 0.23.3 bump for the WASM build; that pin does not change the `v2/` paths.

## Progressive readiness

`initialize()` fetches both bodies with `Promise.all` and compiles WASM on the main thread. `setProcessor` awaits `init`, which awaits that work. Room signaling must not.

```text
connect() ──► room is up, mic muted or NS bypassed
                ├─► fetch pair ──► ok ──► setProcessor, then publish, then setEnabled(true)
                └─► fetch pair ──► err ──► telemetry, stay bypassed or APM-only
```

A practical policy is still the README order once assets are hot: construct, `setProcessor`, `publishTrack`. The failure to avoid is awaiting the cold CDN **inside** `connect()` before the user is in the room. Show “enhancing audio” from byte progress if you measure it. Toast once on failure.

## HTTP caching

An immutable version directory can use `Cache-Control: public, max-age=31536000, immutable`. When bytes change, publish a new directory and let the package prefix point at it. Do not mutate bytes at a URL you marked immutable. `?t=Date.now()` on every join destroys the hit rate. If you also use the Cache API, key by the full versioned URL, cap storage, and offer a support action that clears the noise-suppression cache.

Serve `df_bg.wasm` as `Content-Type: application/wasm`. A missing `Access-Control-Allow-Origin` looks like a generic network error; log status and response type. WASM and the archive are one atomic pair. A 1.3.0 SIMD module beside a 1.1.2-era archive is not a mixed configuration you should “try.”

Regional latency matters on mobile networks. Mirror into a customer VPC when the public host is blocked. CORS and TLS still apply. There is no unpublished authentication header in this public API: the client issues a normal `fetch`.

## Partial failure

| Failure | What the user sees | Action |
|---------|--------------------|--------|
| 404 on WASM or model | Suppression unavailable | Fix the path; publish raw audio |
| CORS error | Same | Fix CDN headers |
| Truncated body | `initialize` throws | Retry once, then bypass |
| Offline after a good cache | May still work | Confirm disk cache or Cache API |
| Mismatched pair | Bad audio or a compile error | Lock both files to one directory |
| Wrong MIME | Streaming loaders fail | `application/wasm` |

## Worked mirror

Download the upstream `DeepFilterNet3_onnx.tar.gz` and the `df_bg.wasm` that matches your package generation. For a client that follows the README’s ≥ 1.2.0 rule, upload to `https://assets.example.com/ns/df3/v2/pkg/` and `.../v2/models/`, and set `cdnUrl` to `https://assets.example.com/ns/df3`. Smoke-test a cold profile with the cache disabled, then again with the cache enabled.

## Mini-lab

Given `cdnUrl = https://example.com/df3`, compute the paths for ≤ 1.1.2 and for ≥ 1.2.0 including 1.3.0. Run `python3 cdn_urls.py`.

```python
cdn = "https://example.com/df3"
pairs = {
    "1.1.2": ("pkg/df_bg.wasm", "models/DeepFilterNet3_onnx.tar.gz"),
    "1.3.0": ("v2/pkg/df_bg.wasm", "v2/models/DeepFilterNet3_onnx.tar.gz"),
}
for ver, (wasm, model) in pairs.items():
    print(ver)
    print(f"{cdn}/{wasm}")
    print(f"{cdn}/{model}")
```

**Expected**

```text
1.1.2
https://example.com/df3/pkg/df_bg.wasm
https://example.com/df3/models/DeepFilterNet3_onnx.tar.gz
1.3.0
https://example.com/df3/v2/pkg/df_bg.wasm
https://example.com/df3/v2/models/DeepFilterNet3_onnx.tar.gz
```

**Failure modes**

- Embedding `v2` in `cdnUrl`, which yields `https://example.com/df3/v2/v2/pkg/df_bg.wasm`.
- Using a filename that is not `df_bg.wasm` or `DeepFilterNet3_onnx.tar.gz`.
- Blocking `connect()` until all four hypothetical URLs respond. Only the two URLs for the installed version are fetched, and not as a gate on signaling.
- Treating 1.3.0 as a no-prefix layout. From 1.2.0 onward, including 1.3.0, the client adds `v2/`.

## Pitfalls

1. Double prefix.
2. Join UI gated on `fetch`.
3. Uploading raw audio from production.
4. One folder shared blindly by ≤ 1.1.2 and ≥ 1.2.0 clients.
5. Wrong WASM MIME type.

## Exercises

1. Repeat the four URLs from memory, then diff against the expected block.
2. List UI states `idle`, `downloading`, `ready`, `error` and which processor method runs on `ready`.
3. Write `Cache-Control` for an immutable `v2` tree and the rule for publishing a new tree.
4. Ten lines of policy for a failed asset load that still leaves the room usable.
5. Why are the WASM file and the tar.gz required to share a directory generation?

### Answer hints

1. Two files times two generations. Prefix only on ≥ 1.2.0 / 1.3.0 README. Base stays `https://example.com/df3`.
2. `ready` is when `initialize()` has resolved. Then `setProcessor` (if you have not already) and `await setEnabled(true)` if the user wanted suppression.
3. `public, max-age=31536000, immutable` on the versioned tree. New bytes get a new directory, not an overwrite.
4. Catch the `setProcessor` or `initialize` rejection, publish the raw track, emit one telemetry reason, do not retry forever.
5. SIMD WASM and the archive are a matched pair. Split generations across folders and you will compile a module against the wrong weights.

## Further reading

- Package README, Custom CDN: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- MDN [HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching) and [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).
- Upstream [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Chapter 06 for quantization, SIMD, and packaging of the same pair.
