---
layout: post
title: "07-02 LiveKit TrackProcessor patterns"
chapter: "07"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter07
lesson_type: required
draft: false
---

LiveKit's client SDKs expose a **TrackProcessor** hook so you can transform a local audio track before it is encoded and published. Mezon's `deepfilternet3-noise-filter` package implements that hook with DeepFilterNet3. This lesson teaches the lifecycle, failure modes, and observability — techniques you can re-apply even if you swap models later.

## 60-minute teaching plan

- 0–10 min: What TrackProcessor owns vs what the Room owns.
- 10–25 min: Lifecycle — construct → init assets → `setProcessor` → process → dispose.
- 25–40 min: Backpressure, enable/disable, suppression level knobs.
- 40–50 min: Mobile browser caveats and observability hooks.
- 50–60 min: Mini-lab: sequence diagram for join / leave / toggle NS.

## Learning objectives

By the end of this lesson, you can:

- Explain TrackProcessor responsibilities in a LiveKit publish path.
- Sketch a DF3 processor lifecycle (init, process, dispose).
- Identify backpressure and failure handling that keeps the call alive.
- Name per-track vs room-level configuration tradeoffs.

## TrackProcessor responsibilities

A processor should:

1. Accept a source track (or attach via `LocalAudioTrack.setProcessor`).
2. Produce a processed track that LiveKit can publish.
3. Load heavy assets (WASM, ONNX/tar model) **asynchronously** with clear ready/error states.
4. Expose runtime controls (`setEnabled`, `setSuppressionLevel`) without republishing when possible.
5. **Dispose** cleanly: terminate workers, close AudioContexts, drop WASM memory.

A processor should *not*:

- Own room signaling or token auth.
- Upload mic PCM to a server for inference in the default Mezon design (on-device inference).
- Silently block the join UI for tens of seconds without progress feedback.

## Reference integration (from package README)

```javascript
import { DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";

const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl:
      "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3",
  },
});

await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);

// Runtime controls
filter.setSuppressionLevel(60);
filter.setEnabled(false);
```

Teaching points:

- `sampleRate: 48000` matches DF3's common full-band framing.
- `noiseReductionLevel` / `setSuppressionLevel` map to product UX ("low / medium / high"), not magic SNR.
- CDN URL is optional but critical for production caching (lesson 07-03).

Lower-level alternative in the same package: `DeepFilterNet3Core` + `createAudioWorkletNode` for non-LiveKit WebAudio graphs.

## Lifecycle state machine

```text
Created
  → LoadingAssets (WASM + model)
  → Ready
  → Active (enabled=true, frames flowing)
  → Bypassed (enabled=false, passthrough or APM-only)
  → Failed (asset error) → fallback path
  → Disposed
```

**Recommended product behavior on Failed:** publish unprocessed (or APM-only) audio and show a non-blocking toast — never fail the entire `connect()`.

### Init

- Start asset fetch early (after auth, before user unmutes) when UX allows.
- Gate "NS ready" separately from "room connected".

### Process

- Honor AudioWorklet timing; never do heavy JS on the main thread per 10 ms quantum (Chapter 05).
- If a frame overruns, drop to passthrough for that quantum rather than queueing unbounded PCM (backpressure).

### Dispose

Call destroy/dispose on:

- `RoomEvent.Disconnected`
- React unmount / route leave
- processor swap (new model version)

## Per-track vs room-level configuration

| Scope | Example | Use when |
|-------|---------|----------|
| Per-track | `setProcessor` on mic track | Default; multiple local tracks rare |
| Room/UX level | "NS on" toggle in settings | Persist preference; apply on next publish |
| Per-participant remote | processing subscribed tracks | Costly; usually for accessibility / recording bots |

Persist user preference (e.g. localStorage) at room/UX level; apply by constructing the processor when creating the local audio track.

## Backpressure and failure handling

1. **Asset timeout:** abort fetch, mark Failed, fallback.
2. **WASM OOM / unsupported SIMD:** detect at init; offer non-SIMD build or disable NS (package ≥1.2.0 targets SIMD browsers).
3. **Underrun:** log RTF/p99; temporarily lower suppression or disable NS.
4. **Race:** user toggles NS while loading — queue the intent; do not double-`setProcessor`.

Pseudo-policy:

```text
onAssetError → enabled=false, publish raw, emit telemetry("ns_asset_error")
onRtHigh → emit telemetry; if sustained, auto-downgrade level or disable
```

## Mobile browser caveats

- Background tabs may throttle timers; audio callbacks are more privileged but not free.
- iOS Safari: AudioContext resume requires user gesture; initialize after tap-to-join.
- Thermals: sustained DF3 + camera + encode can thermal-throttle; measure on mid-tier phones.
- Bluetooth SCO sample rates can differ; stick to documented 48 kHz path when possible.

## Observability hooks

Minimum product telemetry (no raw audio!):

- `ns_init_ms`, `ns_asset_bytes`, `ns_asset_cache_hit`
- `ns_enabled`, `ns_level`
- `ns_rtf_p50/p95` (if measurable)
- `ns_fallback_reason`

Pair with Chapter 08 metrics offline; in-call telemetry is for reliability, not MOS.

## Common pitfalls

1. Calling `setProcessor` before the track exists.
2. Forgetting dispose → zombie worklets after navigation.
3. Blocking join on model download on slow networks.
4. Treating README snippets as the only API — read TypeScript typings in the installed package.

## Exercises

1. Draw the state machine above and mark where your UI shows a spinner vs a toggle.
2. Write a falling-back `connectWithNS()` pseudocode that never rejects solely due to CDN failure.
3. List which events in LiveKit client SDK should trigger dispose in your app.
4. Compare `DeepFilterNoiseFilterProcessor` vs `DeepFilterNet3Core`: when is each appropriate?

## Further reading

- LiveKit docs: Track Processor / local track processing (client SDK docs for your version).
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) README — LiveKit integration section.
- npm package [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- Course Chapter 05 (worklets) and 06 (WASM/SIMD).
