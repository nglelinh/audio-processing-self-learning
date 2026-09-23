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

The TypeScript/WASM package remains the supported browser distribution. A **sibling Rust workspace** (`df-core`, `df-audio`, `df-cli`) explores desktop/server-native DeepFilterNet3 with a frame API mirroring the WASM bindings. This path is **optional stretch** for the capstone — teach milestones and parity discipline, not a mandatory rewrite.

## 60-minute teaching plan

- 0–10 min: Why native (embedding, CLI, shared libs).
- 10–25 min: Frame API map TS → Rust.
- 25–40 min: Backend choices (stub → tract / libDF).
- 40–50 min: Golden tests and licensing/weights.
- 50–60 min: Milestone plan you could finish in 1–2 weeks.

## Learning objectives

By the end of this lesson, you can:

- State goals for a Rust `df-core` experiment (ORT/tract/libDF).
- List FFI / embedding options at a high level.
- Mark this path as optional stretch work.
- Write a parity-test plan against the JS/WASM path.

## Workspace layout (reference)

```text
mezon-noise-suppression-rust/
  crates/df-core   # frame API (create, process_frame, atten…)
  crates/df-audio  # cpal + ringbuf skeleton
  crates/df-cli    # offline WAV CLI
  models/          # place DeepFilterNet3_onnx.tar.gz (do NOT commit)
```

Stub defaults documented in-tree: **480** samples @ **48 kHz** (10 ms) until goldens confirm WASM parity.

## Frame API map

| TypeScript (`df.d.ts` style) | Rust `df-core` |
|------------------------------|----------------|
| `df_create(bytes, atten_lim)` | `DfState::create` / `create_from_path` / `create_stub` |
| `df_get_frame_length(st)` | `DfState::frame_length` |
| `df_process_frame(st, input)` | `DfState::process_frame` → `(Vec<f32>, snr)` |
| `df_set_atten_lim` | `DfState::set_atten_lim` |
| `df_set_post_filter_beta` | `DfState::set_post_filter_beta` |

## Backend milestones (technique checklist)

1. **Stub passthrough** — builds everywhere; validates framing/API. *(often already present)*  
2. **Model path validation** — refuse missing tar/onnx; clear errors.  
3. **Load ONNX** via **tract** *or* link upstream **libDF** / `deep_filter`.  
4. **Match** frame length, hop, sample rate to WASM.  
5. **Return** local SNR when the real model provides it.  
6. **Golden tests** — short WAV fixtures; sample-wise tolerance vs WASM.  
7. **df-cli** enhance files for Chapter 08 harness.  
8. **df-audio** duplex callbacks; measure latency.  
9. Optional **cdylib** FFI for other native hosts.

## Why Rust here?

- Deterministic desktop/server tooling without browser constraints  
- Easier embedding in native meeting clients  
- Shared library potential for non-JS hosts  
- Learning on-device runtimes (tract/ORT) from Chapter 06  

## Licensing and weights

- Follow upstream DeepFilterNet dual license (**Apache-2.0 OR MIT**) as used by the npm package.  
- **Do not commit** large model binaries to git; document download URL.  
- CDN asset used by npm ≥1.2.0 under `v2/models/` is the same family of weights.

## Parity tests (minimum)

```text
fixtures/: clean.wav, noisy.wav
run WASM path → enh_wasm.wav
run df-cli     → enh_rust.wav
compare: SI-SDR(enh_wasm, enh_rust) high / MAE per sample within tolerance
also compare: frame_length, atten behavior smoke tests
```

Until a real backend exists, mark goldens as **pending** — do not fake bit-exact claims.

## Common pitfalls

1. Treating stub passthrough as "NS works".
2. Committing `DeepFilterNet3_onnx.tar.gz` to git.  
3. Making Rust rewrite mandatory for course pass.  
4. Skipping license attribution.

## Exercises

1. Write a 5-bullet milestone plan with time estimates.  
2. Sketch `process_frame` contract tests that do not need a model.  
3. Explain tract vs libDF tradeoff in your own words.  
4. Decide go/no-go: is Rust stretch in *your* capstone? Why?

## Further reading

- In-tree Rust README (workspace build notes).  
- [tract](https://github.com/sonos/tract) / ONNX Runtime Rust docs.  
- Upstream [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) `libDF` / models.  
- Chapter 06 (ONNX, quantization, WASM).
