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

A great ONNX graph still fails productization if **packaging** is wrong: multi-megabyte downloads on 3G, uncached CDN paths, mismatched versions, or licenses. This lesson covers artifact layout, compression, versioning, integrity checks, and constraints that shape Mezon’s npm/CDN delivery (expanded in Ch. 07).

## Learning objectives

You will design a model package directory layout with semver, choose compression and cache headers at a high level, specify integrity hashes and compatibility matrix (opset ↔ runtime), and list legal/privacy constraints for redistributing weights.

## 60-minute teaching plan

- **0–10 min** — Horror story: app update ships FP32 80 MB model, uninstalls spike.
- **10–25 min** — Artifact contents: onnx, config, licenses, changelog.
- **25–40 min** — Size budgets, compression, quantization interplay.
- **40–50 min** — Versioning & integrity; staged rollout.
- **50–60 min** — Pitfalls, exercises, checklist.

## Core explanation

### Suggested layout

```text
models/df3-mono-48k/
  model.onnx              # or .ort optimized
  config.json             # hop, sample_rate, state shapes
  LICENSE_WEIGHTS.txt
  SHA256SUMS
  CHANGELOG.md
```

`config.json` must include sample rate, hop/window, input names, and state tensor shapes so wrappers cannot silently desync.

### Size budgets (teaching defaults — tune per product)

| Channel | Aggressive budget | Notes |
|---------|-------------------|-------|
| Mobile web first load | ≤ 5–10 MB compressed | Prefer INT8 / smaller variant |
| Desktop Electron | ≤ 20–40 MB | Can lazy-download |
| Native mobile app | ship in binary or on-demand | Watch App Store sizes |

Quantization (06-02) and ultra-light alternatives (04-05) are packaging decisions as much as ML decisions.

### Compression & caching

- Serve with Brotli/gzip; ONNX often compresses well.
- Content-hash filenames (`model.onnx` → `model.abc123.onnx`) for immutable CDN cache.
- `Cache-Control: immutable` for hashed assets; short cache for `latest` pointers.

### Integrity & compatibility

1. Publish SHA-256; verify after download.
2. Matrix-test: ORT 1.x + model opset + browser matrix in CI.
3. Refuse to run if `config.json` semver major ≠ wrapper major.

### Legal / ethical packaging

- Respect weight licenses (academic non-commercial vs commercial).
- Document third-party notices (ORT, model authors).
- Do not bundle customer audio in packages.
- GDPR-style: models aren’t personal data, but telemetry of voice metrics may be.

### Staged rollout

Canary 5% of desktop clients → watch underrun metrics → expand. Keep previous model version on CDN for rollback.

## Packaging checklist (ship gate)

- [ ] `config.json` complete and tested
- [ ] SHA256 published
- [ ] License files present
- [ ] RTF_p95 pass on target tier
- [ ] Listening gate vs previous version
- [ ] CDN cache verified
- [ ] Rollback path documented

## Pitfalls

- Overwriting `model.onnx` in place (cache poisoning hell).
- Forgetting that npm package size ≠ CDN model size (split them).
- No `config` → silent hop mismatch after “successful” load.
- Shipping debug ORT builds to production.

## Exercises

1. **Write a config schema.** JSON Schema or typed struct for Mezon model config.
2. **Budget table.** Propose sizes for web vs native given DF3 FP32 vs INT8.
3. **Rollback drill.** Document steps to revert model version in <15 minutes.
4. **License audit.** List license questions you must answer before redistributing DeepFilterNet weights commercially.

## Further reading

- ONNX Runtime packaging / model optimization docs (`ORT` format).
- npm package size best practices; CDN caching guides.
- DeepFilterNet / model card license sections (primary sources).
- Chapter 07 lessons on CDN loading and Mezon npm surface.
