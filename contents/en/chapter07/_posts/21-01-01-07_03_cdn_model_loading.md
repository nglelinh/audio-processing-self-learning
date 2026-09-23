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

DeepFilterNet3 in the browser needs **WASM** plus a **model archive** (`DeepFilterNet3_onnx.tar.gz`). Shipping those only inside npm tarball bloats installs and slows first paint; production apps usually load them from a **CDN** with caching and versioned paths. This lesson designs progressive download, cache safety, and failure modes that keep the call up.

## 60-minute teaching plan

- 0–10 min: What must be fetched (WASM vs model) and approximate sizes.
- 10–25 min: Mezon `assetConfig.cdnUrl` and `v2/` path rules (≥1.2.0).
- 25–40 min: HTTP caching, content hashing, cache busting.
- 40–50 min: Progressive UX — readiness without blocking connect.
- 50–60 min: Mini-lab: failure matrix (404, CORS, offline, stale cache).

## Learning objectives

By the end of this lesson, you can:

- Design progressive download with user-visible readiness.
- Cache models safely across sessions.
- Handle partial failures without killing the call.
- Explain why ≥1.2.0 appends `v2/` under your CDN base URL.

## Assets involved

From the `deepfilternet3-noise-filter` README:

| Asset | Role |
|-------|------|
| `pkg/df_bg.wasm` (under base or `v2/`) | Native-speed DSP/inference glue |
| `models/DeepFilterNet3_onnx.tar.gz` | Model weights / graph archive from upstream DeepFilterNet |

Upstream model pointer: [Rikorose/DeepFilterNet `DeepFilterNet3_onnx.tar.gz`](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).

**Privacy:** default Mezon design runs inference **on-device**. CDN serves *weights*, not user audio. Do not "helpfully" upload PCM to a server unless you have an explicit product + consent path.

## Configuring the CDN base

```javascript
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  assetConfig: {
    cdnUrl:
      "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3",
  },
});
```

### Version-specific paths

| Package version | Resolved paths |
|-----------------|----------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm`, `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| ≥ 1.2.0 | `{cdnUrl}/v2/pkg/df_bg.wasm`, `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |

The `v2/` prefix is added **by the package** for ≥1.2.0 — do **not** put `v2` in `cdnUrl` yourself or you risk `.../v2/v2/...`.

SIMD builds (≥1.2.0) need browsers with WASM SIMD (Chrome 91+, Firefox 89+, Safari 16.4+ per package notes).

## Progressive download and readiness UX

Recommended sequence:

1. **Room connect** proceeds with mic muted or NS bypassed.
2. Background fetch WASM + model; show "Enhancing audio…" progress if you can measure bytes.
3. On success → enable processor / unmute with NS.
4. On failure → stay on APM-only or raw mic; toast once.

```text
connect() ──► publish (NS bypassed)
                │
                ├─► fetch assets ──► ok ──► setEnabled(true)
                │
                └─► fetch assets ──► err ──► telemetry + stay bypassed
```

Never make `await fetch(model)` the gate for WebSocket join on mobile networks.

## HTTP caching and cache busting

### Desired browser/CDN behavior

- **Immutable versioned URL** (best): `/deepfilternet3/v2/...` with long `Cache-Control: public, max-age=31536000, immutable`.
- When weights change, publish a **new path** (v3) or new package major that points elsewhere — do not silently mutate bytes at an immutable URL.

### Cache busting anti-patterns

- Query `?t=Date.now()` on every load — destroys CDN hit rate.
- Same URL, new bytes, short max-age only — works but wastes bandwidth; prefer versioned directories.

### Service workers / Cache API (optional)

If you cache models in Cache Storage:

- Key by full URL including version segment.
- Cap storage; model archives are large.
- Provide an "Clear NS cache" support action.

## Regional CDN considerations

- Put the origin close to users (or use a multi-region CDN).
- Measure TTFB and total download on Viet Nam / SEA mobile networks — first-session NS delay is a product metric.
- Mirror for enterprise VPC if customers block public CDN hosts (CORS + TLS still required).

### CORS

WASM and model fetches from a different origin need correct `Access-Control-Allow-Origin`. A missing CORS header presents as a generic failure in JS — log status and response type in telemetry.

## Partial failure matrix

| Failure | User-visible | Engineering action |
|---------|--------------|--------------------|
| 404 on wasm | NS unavailable | Fix deploy; fallback audio |
| 404 on model | NS unavailable | Same |
| CORS error | NS unavailable | Fix CDN headers |
| Truncated download | init error | retry once; then fallback |
| Offline after cached | may work | verify Cache API / HTTP disk cache |
| Stale incompatible wasm/model pair | crashes / bad audio | version lock both under same `v2/` |

**Atomicity:** treat WASM + model as a **pair** released together under one version directory.

## Worked example: private mirror

1. Download upstream `DeepFilterNet3_onnx.tar.gz` and your built `df_bg.wasm`.
2. Upload to `https://assets.example.com/ns/df3/v2/pkg/` and `.../v2/models/`.
3. Set `cdnUrl: "https://assets.example.com/ns/df3"` with package ≥1.2.0.
4. Smoke-test: cold browser profile, DevTools disabled cache off/on, verify single download then 304/disk cache.

## Common pitfalls

1. Double `v2` in the path.
2. Blocking UI on model fetch.
3. Logging or uploading raw audio "for debugging" from production clients.
4. Mixing ≤1.1.2 layout with ≥1.2.0 clients on one CDN folder.
5. Forgetting `Content-Type` / compression issues on `.wasm` (serve correct MIME).

## Exercises

1. Given `cdnUrl = https://example.com/df3`, write the four full URLs for package 1.1.2 vs 1.3.0.
2. Design a readiness UI state list: `idle | downloading | ready | error`.
3. Propose Cache-Control headers for an immutable `v2` tree.
4. Write a fallback policy in 10 lines of pseudocode for asset load failure.

## Further reading

- Package README: Custom CDN Configuration — [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- MDN: [HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching), [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).
- Upstream model: [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Course Chapter 06 (WASM/SIMD packaging).
