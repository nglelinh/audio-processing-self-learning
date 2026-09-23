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

The npm package `deepfilternet3-noise-filter` **1.3.0** is a vehicle for DeepFilterNet3 in LiveKit and Web Audio apps. It is not the syllabus. This lesson maps the public methods onto frames, gains, WASM, the CDN, and LiveKit’s `TrackProcessor`, so a capstone changes a technique you can measure. Course tasks do not modify the product repository. An optional instructor checkout is `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

![Public processor API in front of a LiveKit TrackProcessor publish path]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. The npm surface is a TrackProcessor plus a Web Audio core, not a second noise-suppression algorithm.*

## Learning objectives

You will map each public call onto a course idea, choose configure versus fork with a maintenance argument, and name extension work that needs zero edits inside the product tree.

## 60-minute teaching plan

- **0–10 min** — Core, TrackProcessor, assets.
- **10–25 min** — API table against Chapters 02–06.
- **25–40 min** — Knobs: level, bypass, CDN, SIMD.
- **40–50 min** — Configure, wrap, or fork.
- **50–60 min** — Mini-lab and capstone constraints.

## Public surface

Install with `npm install deepfilternet3-noise-filter`. Peer dependency: `livekit-client` ^2. The README’s bundler note still holds: worklet code is inlined as blob URLs, so a copy plugin is not required.

### `DeepFilterNoiseFilterProcessor`

LiveKit `TrackProcessor` implementation. `name` is `deepfilternet3-noise-filter`.

- Constructor options: `sampleRate`, `noiseReductionLevel`, `enabled`, `assetConfig.cdnUrl`.
- `static isSupported()` — `AudioContext` and `WebAssembly` exist.
- `init` and `restart` — build or rebuild the 48 kHz graph on a `MediaStreamTrack`.
- `setSuppressionLevel(level)` — forwards 0–100 to the core.
- `await setEnabled(boolean)` — bypass or resume suppression; returns the enabled flag.
- `suspend`, `resume` — `AudioContext` power states.
- `destroy` — tear down the graph and the core.
- Attach with `await audioTrack.setProcessor(filter)`, then `publishTrack`.

`DeepFilterNoiseFilter(options)` is a small factory that returns a processor. Prefer the class in course snippets so the lifecycle stays visible.

### `DeepFilterNet3Core`

Web Audio core used by the processor and usable alone:

```javascript
import { DeepFilterNet3Core, DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";

const proc = new DeepFilterNet3Core({ sampleRate: 48000, noiseReductionLevel: 0 });
await proc.initialize();
const node = await proc.createAudioWorkletNode(ctx);
proc.setSuppressionLevel(50); // 0–100
proc.setNoiseSuppressionEnabled(true);
proc.destroy();
```

`initialize` fetches and compiles. `createAudioWorkletNode` throws if you skipped it. `setNoiseSuppressionEnabled(false)` is the core’s bypass; the processor’s `setEnabled` calls it. `destroy` drops the worklet and the compiled assets.

### Assets

`df_bg.wasm` is the WASM build described in the README (`wasm-pack`, SIMD flags for ≥ 1.2.0). `DeepFilterNet3_onnx.tar.gz` is the upstream archive. The 1.3.0 changelog records a tract **0.23.3** bump for that WASM path. CDN layout is lesson 07-03. Repository: [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).

## API to course idea

| API or artifact | Course idea |
|-----------------|-------------|
| 48 kHz `sampleRate` | Chapter 02 PCM and full-band speech |
| AudioWorklet node | Chapter 05 realtime callback |
| Frame inside WASM | Chapter 02 hop; DeepFilter ERB and deep filter, Chapter 04 |
| `noiseReductionLevel` 0–100 | Gain aggressiveness, not a promise about SI-SDR |
| CDN `cdnUrl` | Chapter 06 packaging and lesson 07-03 |
| SIMD WASM ≥ 1.2.0 | Chapter 06; README’s 20–30% claim |
| `setProcessor` | Lesson 07-01 insertion point A |
| `await setEnabled(false)` | Bypass without a second publish |
| INT8 weights, if you quantize offline | Lesson 06-02, done before upload |

There is no public method that sets an ONNX input name, an opset, or a private server route. If a capstone needs a new graph, that is a fork or a separate runtime, not a hidden option.

Optional native mirror, stretch only: a Rust `df-core` frame API in the Rust sibling, Chapter 09. Do not block the browser capstone on it.

## Knobs

| Knob | Turn up | Risk |
|------|---------|------|
| Suppression level | Lower noise floor | Thin voice, musical noise near zero gains |
| Enabled | Suppression on | CPU, thermals, delay |
| CDN versus bundled bytes | Shared cache, smaller npm install | First-join network dependency |
| SIMD build | Lower real-time factor where it instantiates | Safari before 16.4 fails closed |

Pair every knob change with Chapter 08 (SI-SDR on synthetic mixes, DNSMOS or a short listening test on real clips) and a real-time factor on a named device. A dependency bump with no table is not a result.

## Extension without editing the product

1. An evaluation harness: WAV in, WAV out, SI-SDR and DNSMOS.
2. UX policy: disable suppression for music mode or when real-time factor stays high.
3. Your own CDN layout and cache headers.
4. Telemetry of init time and fallback reason, no audio upload.
5. A written fork plan if the loader cannot host a different archive.
6. Stretch: frame-API parity in Rust `df-core`.

## Configure versus fork

| Situation | Prefer |
|-----------|--------|
| CDN base, default level, enable UX | Configure `assetConfig` and the constructor |
| Lifecycle bug or LiveKit version skew | Report upstream, or a thin wrapper in your app |
| New model architecture | Fork or a new package; keep Apache-2.0 OR MIT, matching upstream |
| Course homework | Your repo, your notes, or the Rust sibling. Not the instructor product tree |

## Annotated join path

```javascript
// 07-01 insertion A, local pre-encode
// 07-03 CDN; client prefixes v2 for the README’s >= 1.2.0 rule
// 05 AudioWorklet inside init
// 04 DeepFilterNet3 weights in the tar.gz
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: { cdnUrl: MY_CDN },
});
await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);
filter.setSuppressionLevel(60);
```

## Mini-lab

Run `python3 api_map.py`. It binds each call to the type that owns it in 1.3.0.

```python
calls = {
    "createAudioWorkletNode": "DeepFilterNet3Core",
    "setProcessor": "LiveKit LocalAudioTrack",
    "setEnabled": "DeepFilterNoiseFilterProcessor",
    "setNoiseSuppressionEnabled": "DeepFilterNet3Core",
    "isSupported": "DeepFilterNoiseFilterProcessor",
}
for name in sorted(calls):
    print(f"{name} -> {calls[name]}")
```

**Expected**

```text
createAudioWorkletNode -> DeepFilterNet3Core
isSupported -> DeepFilterNoiseFilterProcessor
setEnabled -> DeepFilterNoiseFilterProcessor
setNoiseSuppressionEnabled -> DeepFilterNet3Core
setProcessor -> LiveKit LocalAudioTrack
```

**Failure modes**

- Calling `setEnabled` on the core. The core method is `setNoiseSuppressionEnabled`.
- Calling `setNoiseSuppressionEnabled` on the processor. The processor method is `setEnabled`, and it should be awaited.
- Treating `setProcessor` as a method of the npm class. It is `LocalAudioTrack.setProcessor`.
- Editing `/Users/nguyenlelinh/ncc/mezon-noise-suppression` as part of the exercise.

## Pitfalls

1. A capstone that only bumps the dependency.
2. Blaming the model for a double-prefix CDN 404.
3. Redistributing weights without reading the upstream license.
4. Course commits inside the product tree.

## Exercises

1. Extend the mini-lab table with `init`, `restart`, `destroy`, and `setSuppressionLevel`.
2. Propose one capstone improvement that needs zero package source changes, and name the metric.
3. Propose one improvement that needs a fork, and justify why configuration cannot do it.
4. Compare suppression levels 40 and 80 on one noisy clip. What do you listen for near quiet bins?
5. Why does `isSupported()` returning true not authorize you to skip the Safari 16.4 check?

### Answer hints

1. `init`, `restart`, and `destroy` are on the processor (LiveKit calls `init` / `restart`). `setSuppressionLevel` exists on both; the processor forwards to the core.
2. A CDN mirror, a bypass policy, or an SI-SDR harness around WAV files. Metric: SI-SDR delta, DNSMOS, or real-time factor p95.
3. A new operator set or a different archive layout the loader cannot express. Configuration only sets sample rate, level, enabled, and `cdnUrl`.
4. Level 80 should cut more noise and may thin fricatives or musical-noise the floor. Level 40 leaves more residual. Use the same clip.
5. `isSupported()` checks `AudioContext` and `WebAssembly` only. SIMD is lesson 06-03; Safari before 16.4 fails the ≥ 1.2.0 module at compile time.

## Further reading

- npm [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter) and [GitHub](https://github.com/mezonai/mezon-noise-suppression).
- Upstream [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet), including Schröter et al., ICASSP 2022, arXiv:2110.05588.
- LiveKit [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/).
- [tract](https://github.com/sonos/tract) and [ONNX Runtime](https://onnxruntime.ai/docs/) for the runtime side of Chapter 06.
