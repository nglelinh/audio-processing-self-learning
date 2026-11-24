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

In a real video-conferencing app like LiveKit or Mezon, users don’t just join a call once and sit still: they plug in AirPods mid-sentence, switch from laptop mic to USB Yeti, toggle noise suppression on and off, and bounce between voice channels. If your audio processor doesn’t implement a rock-solid **TrackProcessor lifecycle (`init`, `restart`, `destroy`)**, every microphone switch leaks megabytes of WASM linear memory and leaves zombie `AudioWorklet` nodes burning CPU in the background!

This lecture breaks down the **LiveKit `TrackProcessor` pattern**: how LiveKit hands your processor a raw `MediaStreamTrack` and expects a `processedTrack` back, how to cleanly reset streaming state on `restart()`, and how to guarantee deterministic teardown on `destroy()`.

---

## Background Knowledge Map: Track Lifecycle, Resource Ownership, and Zero-Leak Teardown

Building a production-grade `TrackProcessor` rests on four lifecycle guarantees:

1. **The `TrackProcessor` Interface Contract:** LiveKit calls `init(opts)` when attaching to a `LocalAudioTrack`, `restart(opts)` when the underlying hardware microphone or constraints change, and `destroy()` when the track unpublishes or the user leaves the room.
2. **Deterministic Resource Ownership (No Zombie AudioContexts):** Each `AudioContext`, `AudioWorkletNode`, Web Worker, and WASM instance holds native OS threads and heap buffers that JavaScript’s garbage collector will *not* reclaim until explicitly `.disconnect()`, `.terminate()`, and `.close()`d!
3. **State Reset vs. Engine Reuse on `restart()`:** Switching from a 48 kHz built-in mic to a 16 kHz Bluetooth headset changes the source track—you should keep the compiled WASM module cached, reconnect the new `MediaStreamAudioSourceNode`, and zero out all GRU/conv streaming states so old audio doesn’t bleed into the new mic.
4. **Seamless Bypass Without Re-Negotiating WebRTC:** Toggling NS off/on should route audio around the denoiser *inside* the same `processedTrack` rather than replacing the WebRTC sender track (avoiding SDP renegotiation hiccups).

---

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
import { DeepFilterNoiseFilter, DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";
// DeepFilterNoiseFilter(options) returns a DeepFilterNoiseFilterProcessor.

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

---

### Worked Numerical Example: Quantifying Memory & CPU Leaks Across 5 Device Switches

Suppose one instance of your WASM denoiser + Worker + `AudioContext` allocates:
- WASM linear memory + model weights: **8.0 MB**
- Worker thread + ring buffers: **2.5 MB**
- Idle audio callback overhead: **1.5% CPU**

Compare a buggy `restart()` (that forgets to close old nodes/workers) against a disciplined lifecycle across 5 mic switches during a long meeting:

| Lifecycle Metric | Buggy `restart()` (No Cleanup) | Clean `restart()` (Reuse Engine + Reset State) |
| :--- | :--- | :--- |
| Live WASM/Worker Memory | $$6 	imes 10.5 = \mathbf{63.0	ext{ MB}}$$ (leaked!) | **$$10.5	ext{ MB}$$** (constant $$O(1)$$) |
| Active `AudioContext`s | 6 (hits browser limit of ~6!) | **1** |
| Background CPU Overhead | $$6 	imes 1.5\% = 9.0\%$$ wasted | **$$1.5\%$$** |
| Switch Glitch Duration | 400–800 ms (re-downloading/compiling) | **< 20 ms** (instant state reset) |

Notice that Chrome enforces a hard cap on simultaneous active `AudioContext` instances per tab—forgetting `.close()` on `destroy()` doesn’t just leak RAM; after 6 channel switches it literally **throws an exception and kills the user’s mic**!

### Deep-Dive Explanation: Four Rules for Rock-Solid LiveKit TrackProcessors (Read Slowly)

1. **Make `destroy()` idempotent:** LiveKit or React strict-mode hooks may invoke `destroy()` twice; guarding with `if (this.destroyed) return;` prevents double-free errors on WASM pointers.
2. **Disconnect audio graph nodes in strict reverse order:** Disconnect source $$	o$$ worklet $$	o$$ destination, notify the Worker to free its WASM heap, call `worker.terminate()`, and finally `await audioCtx.close()`.
3. **Zero streaming state on every `restart()` and unmute:** Calling `wasm.reset_state()` clears stale STFT overlap-add tails and GRU hidden states so the first word on the new mic is never clipped.
4. **Expose an instant runtime `setEnabled(bool)` toggle:** Switching between denoised and raw audio inside the worklet (with a 5 ms crossfade) gives users zero-click A/B toggling during a call.

**Quick check.** When a user switches microphones mid-call and LiveKit triggers `restart(opts)`, why is it better to call `reset_state()` and rewire the audio graph than to re-fetch and re-compile the `.wasm` module from scratch?

---

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

## Video tham khảo

- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, English. **xem trước.** LiveKit is an SFU: it forwards tracks without mixing them. This talk is that architecture. It is not a TrackProcessor tutorial; no accurate LiveKit-specific public tutorial survived verification.
- [Revamping Audio Quality for RTC Part 1: Beryl Echo Cancellation | Sriram Srinivasan and Hoang Do](https://www.youtube.com/watch?v=lapq9zvUd-k) — @Scale, English. Local enhancement before encode is the moment a TrackProcessor has to finish. Watch that slot in a production chain.
- [AudioWorklet :: What, Why, and How - Hongchan Choi](https://www.youtube.com/watch?v=g1L4O1smMC0) — WebAudio PDX, English. The processor callback is the thread a LiveKit audio processor still has to obey.
