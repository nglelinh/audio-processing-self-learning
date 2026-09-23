---
layout: post
title: "07-04 Mezon npm surface (techniques, not only wrapper)"
chapter: "07"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter07
lesson_type: required
draft: false
---

The npm package `deepfilternet3-noise-filter` is a **vehicle** for shipping DeepFilterNet3 into LiveKit/WebAudio apps — not the syllabus itself. This lesson maps the public API onto DSP and systems ideas from Chapters 02–06 so your capstone improves *techniques*, not wrapper trivia.

## 60-minute teaching plan

- 0–10 min: Package map — Core vs TrackProcessor vs assets.
- 10–25 min: API → concept table (frames, attenuation, worklet).
- 25–40 min: Knobs that move latency vs quality.
- 40–50 min: Extend vs fork vs configure.
- 50–60 min: Mini-lab: annotate README sample with course chapter links.

## Learning objectives

By the end of this lesson, you can:

- Map npm API calls to underlying DSP/inference concepts.
- List extension points for custom models or runtimes.
- Avoid treating the package as a black box in the capstone.
- Decide configure vs fork with a maintainability argument.

## Public surface (conceptual tour)

From the published README and typings (always verify your installed version):

### `DeepFilterNoiseFilterProcessor`

LiveKit-oriented processor:

- Constructor options: `sampleRate`, `noiseReductionLevel`, `enabled`, `assetConfig.cdnUrl`
- `setSuppressionLevel(level)`
- `setEnabled(boolean)`
- Used via `LocalAudioTrack.setProcessor(processor)`

### `DeepFilterNet3Core`

WebAudio-oriented core:

- `initialize()`
- `createAudioWorkletNode(audioContext)`
- `setSuppressionLevel(level)`
- `destroy()`

### Assets

- WASM (`df_bg.wasm`) built from DeepFilterNet `libDF` via `wasm-pack`
- Model archive from upstream DeepFilterNet3 ONNX tarball

Repo: [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).  
Local instructor path (do not edit from course tasks): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

## API → course concept map

| API / artifact | Course idea |
|----------------|-------------|
| 48 kHz `sampleRate` | Chapter 02 PCM / Nyquist full-band speech |
| Worklet node | Chapter 05 realtime callbacks |
| Frame processing inside WASM | Chapter 02 frames / hop; DF ERB+deep filter (Ch 04) |
| `noiseReductionLevel` / attenuation | Gain limits / post-filter aggressiveness — quality vs artifacts |
| CDN model load | Chapter 06 packaging + 07-03 |
| SIMD WASM ≥1.2.0 | Chapter 06 SIMD |
| LiveKit `setProcessor` | Chapter 07-01/02 insertion point A |

Optional native mirror (stretch): Rust `df-core` frame API (`df_create`, `df_process_frame`, …) in `mezon-noise-suppression-rust` — Chapter 09-03.

## Configuration knobs and tradeoffs

| Knob | Turn up | Risk |
|------|---------|------|
| Suppression level | Cleaner noise floor | Over-attenuation, musical noise, voice thinness |
| Enabled | NS on | CPU / thermals / latency |
| CDN vs bundled | Faster installs / shared cache | Runtime dependency on network first time |
| SIMD build | Lower RTF | Older browser breakage |

**Measurement:** pair any knob change with Chapter 08 metrics (SI-SDR on synthetic sets, DNSMOS on real, short listening test) plus RTF on target devices.

## Extension points (techniques checklist)

Without rewriting the product repo, students can practice:

1. **Eval harness** outside the package — WAV in/out, SI-SDR/DNSMOS tables.
2. **UX policies** — when to disable NS (music mode, CPU pressure).
3. **Asset hosting** — private CDN layout and cache headers.
4. **Telemetry** — init time, fallback rate (no audio upload).
5. **Alternative models** (advanced) — swap ONNX if the loader allows; otherwise document a fork plan.
6. **Native path** — implement `process_frame` parity in Rust `df-core` (optional stretch).

## Configure vs fork

| Situation | Prefer |
|-----------|--------|
| CDN URL, default level, enable UX | Configure |
| Bug in lifecycle / LiveKit version skew | PR upstream or temporary wrap |
| New model architecture | Fork or separate package — keep licenses (Apache-2.0 OR MIT dual, following upstream) |
| Course homework | **Do not** modify product repo; work in your own fork / notes / rust sibling |

## Worked example: annotate a join path

```javascript
// Ch07-01: insertion point A (local pre-encode)
// Ch07-03: assets from CDN (v2 auto for >=1.2.0)
// Ch05: worklet inside the processor
// Ch04: DeepFilterNet3 weights
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,           // Ch02
  noiseReductionLevel: 80,     // start high; validate with listening (Ch08)
  enabled: true,
  assetConfig: { cdnUrl: MY_CDN },
});
await audioTrack.setProcessor(filter); // Ch07-02
```

## Common pitfalls

1. Capstone = "bump dependency" with no measurements.
2. Confusing npm wrapper bugs with model quality issues.
3. Ignoring license / model attribution when redistributing weights.
4. Editing instructor product tree instead of a personal workspace.

## Exercises

1. Build a two-column table: left = README API, right = chapter technique.
2. Propose one capstone improvement that needs **zero** package source changes.
3. Propose one improvement that would need a fork — justify.
4. Read `setSuppressionLevel` behavior on a noisy café recording (informal A/B) at 40 vs 80.

## Further reading

- npm: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter)
- GitHub: [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)
- Upstream: [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (papers + models)
- DeepFilterNet ICASSP 2022 paper (arXiv:2110.05588) — foundational citation used by the package README
