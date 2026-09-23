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

LiveKit’s client SDK exposes a **TrackProcessor** so a local audio track can be transformed before it is encoded and published. `DeepFilterNoiseFilterProcessor` in `deepfilternet3-noise-filter` **1.3.0** is that hook for DeepFilterNet3. The class also implements `init`, `restart`, `suspend`, `resume`, and `destroy`, and a static `isSupported()`. This lesson is the lifecycle, the order of join calls, and the failures that keep a call up when the CDN or the worklet misbehaves.

![TrackProcessor lifecycle from construction through publish on a LiveKit local audio track]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. TrackProcessor sits on the local audio track: init builds the worklet graph, publish sends processedTrack.*

## Learning objectives

You will order `new DeepFilterNoiseFilterProcessor`, `setProcessor`, `publishTrack`, and `setSuppressionLevel`, name the processor methods LiveKit calls for you, and keep `connect()` independent of the model download.

## 60-minute teaching plan

- **0–10 min** — What the processor owns versus what the Room owns.
- **10–25 min** — Lifecycle and the public 1.3.0 snippet.
- **25–40 min** — Enable, bypass, suppression level, backpressure.
- **40–50 min** — Mobile, telemetry, dispose.
- **50–60 min** — Mini-lab on call order.

## Responsibilities

A processor should accept a source track through `LocalAudioTrack.setProcessor`, produce `processedTrack`, load WASM and the model archive asynchronously, expose runtime controls that do not require a republish, and dispose workers, the `AudioContext`, and WASM memory. It should not own room tokens, and it should not upload microphone PCM. The default Mezon path is on-device. It also should not freeze the join button for tens of seconds with no progress.

`DeepFilterNoiseFilterProcessor.isSupported()` returns true when `AudioContext` and `WebAssembly` exist. That is a floor, not a SIMD check (lesson 06-03).

## Reference integration

Peer dependency: `livekit-client` ^2. The public constructor and the call order:

```javascript
import { DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";

const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl: "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3"
  }
});

await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);
filter.setSuppressionLevel(60);
await filter.setEnabled(false); // bypass
```

`sampleRate: 48000` matches the full-band graph this package builds (`new AudioContext({ sampleRate: 48000 })`). `noiseReductionLevel` and `setSuppressionLevel` are a 0–100 product knob, not an SNR target. The level is clamped and forwarded to the worklet port. `setEnabled` is asynchronous. The README sample sometimes omits `await`; the method returns a promise and updates `DeepFilterNet3Core.setNoiseSuppressionEnabled`, which posts a bypass flag. Await it. Bypass leaves the graph in place, so the publish slot does not change.

`setProcessor` is what your code calls. LiveKit then calls `init({ track })`. `init` stores the original track and `ensureGraph`: resume the context, `initialize()` the core (parallel fetch of WASM and model, then `WebAssembly.compile`), create the AudioWorklet node once, connect source → worklet → destination, and assign `processedTrack`. `restart` is the same graph rebuild when the microphone track identity changes. `suspend` and `resume` map onto the `AudioContext`. `destroy` disconnects nodes, closes the context, and calls `processor.destroy()`.

The non-LiveKit twin is `DeepFilterNet3Core`: `initialize`, `createAudioWorkletNode`, `setSuppressionLevel`, `setNoiseSuppressionEnabled`, `destroy`. Use it when you own the `AudioContext` yourself.

## State machine

```text
Created
  → LoadingAssets   (inside init / initialize)
  → Ready
  → Active          (enabled, frames flowing)
  → Bypassed        (await setEnabled(false))
  → Failed          (asset or compile error)
  → Disposed        (destroy)
```

On failure, publish unprocessed or APM-only audio and show a non-blocking toast. Do not reject `connect()` solely because the archive 404s. Gate “suppression ready” separately from “room connected.”

### Backpressure

Honor AudioWorklet timing. A frame that misses its quantum should passthrough or drop, not append to an unbounded PCM queue. Sustained high real-time factor is a reason to lower the suppression level or bypass, not to buffer five seconds of audio.

### Per-track versus room settings

| Scope | Example | Use when |
|-------|---------|----------|
| Per track | `setProcessor` on the mic | Default |
| Room / UX | “NS on” in settings | Persist in localStorage; apply at publish |
| Remote participant | Process subscribed tracks | Rare; bots and recording |

Persist the preference at the UX layer. Apply it by constructing the processor when you create the local track.

## Join order and the CDN

`await audioTrack.setProcessor(filter)` waits for `init`, and `init` waits for the CDN. That is correct **before publish**. It is the wrong thing to put in front of `room.connect()`. Connect the signaling path, publish when you are ready, and if assets are still in flight keep the mic muted or bypassed. Calling `setProcessor` only after `publishTrack`, and then never `restart` when the underlying track is replaced, leaves LiveKit sending the original mic. The safe order is construct, `setProcessor`, `publishTrack`, then `setSuppressionLevel`. A later device change goes through `restart`, not through a second forgotten `setProcessor`.

## Mobile and telemetry

Background tabs throttle timers. Audio callbacks are more privileged and still not free. iOS Safari resumes an `AudioContext` from a user gesture; initialize after tap-to-join. Camera plus this model plus Opus can thermal-throttle a mid-range phone. Bluetooth SCO rates may not be 48 kHz; stay on the documented 48 kHz context when you can.

Telemetry without raw audio: `ns_init_ms`, asset bytes, cache hit, enabled flag, level, real-time factor percentiles, fallback reason. That is reliability data. MOS stays in Chapter 08.

## Mini-lab

Read the snippet above and fill the order. Check yourself with `python3 join_order.py`.

```python
order = [
    "new DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "publishTrack",
    "setSuppressionLevel",
]
print("\n".join(f"{i}. {step}" for i, step in enumerate(order, 1)))
```

**Expected**

```text
1. new DeepFilterNoiseFilterProcessor
2. setProcessor
3. publishTrack
4. setSuppressionLevel
```

**Failure modes**

- Calling `setProcessor` after `publishTrack` without `restart` when the mic track is replaced. The room keeps the unprocessed track.
- Blocking `connect()` on the CDN. Asset fetch belongs to `init` inside `setProcessor`, not to the signaling handshake.
- Forgetting `await` on `setEnabled` and reading `isEnabled()` before the bypass post completes.
- Double `setProcessor` while the first `init` is still fetching.

## Pitfalls

1. `setProcessor` before the `LocalAudioTrack` exists.
2. Navigation without `destroy`, leaving a zombie worklet.
3. Treating the README fragment as the whole API. `init`, `restart`, `suspend`, `resume`, `destroy`, and `isSupported` are real.
4. Using the obsolete class name that is not the 1.3.0 export. Construct `DeepFilterNoiseFilterProcessor` or `DeepFilterNet3Core`.

## Exercises

1. Mark on the state machine where the UI shows a spinner versus a toggle.
2. Sketch `connectWithNS()` that still joins when the CDN fails.
3. List LiveKit events that should call `destroy` in your app.
4. When do you pick `DeepFilterNoiseFilterProcessor` versus `DeepFilterNet3Core`?
5. A user toggles bypass during `LoadingAssets`. What do you store, and which method applies it after `init`?

### Answer hints

1. Spinner during `LoadingAssets`. Toggle only in `Active` and `Bypassed`. `Failed` shows the toast, not a spinner that never ends.
2. `await room.connect(url, token)` with no `await filter` in front of it. Publish raw or APM audio in the `catch` of `setProcessor`.
3. Disconnected, and your own route unmount. Device changes call `restart` rather than a full leave.
4. Processor when a LiveKit `LocalAudioTrack` is published. Core when you build the `AudioContext` graph yourself.
5. Store the desired boolean. `ensureGraph` already ends in `setEnabled(this.enabled)`. Do not call `setProcessor` a second time.

## Further reading

- LiveKit: [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/), and the docs home [https://docs.livekit.io/](https://docs.livekit.io/).
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) and the [npm package](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- Chapter 05 for the worklet quantum and Chapter 06 for SIMD compile failures during `init`.
