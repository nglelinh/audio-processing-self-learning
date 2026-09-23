---
layout: post
title: "07-01 WebRTC insertion points"
chapter: "07"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter07
lesson_type: required
draft: false
---

Where you insert noise suppression (NS) in a WebRTC call decides latency, echo behavior, and whether the SFU ever sees clean speech. This lesson maps the insertion points relative to `getUserMedia`, the browser Audio Processing Module (APM), and `RTCPeerConnection`, then contrasts built-in APM NS with a custom neural path like DeepFilterNet3.

## 60-minute teaching plan

- 0–10 min: Call graph — mic → processing → encode → SFU → decode → render.
- 10–25 min: Insertion points A/B/C (pre-encode local, remote post-decode, SFU-side).
- 25–40 min: Browser APM NS vs custom neural NS (constraints, when to disable APM NS).
- 40–50 min: Track replacement patterns and device-switch pitfalls.
- 50–60 min: Mini-lab sketch: replace a local `MediaStreamTrack` after Neural NS.

## Learning objectives

By the end of this lesson, you can:

- Locate where NS can run relative to `getUserMedia` and `PeerConnection`.
- Compare browser APM NS vs custom neural NS for conferencing.
- List constraints unique to SFU-based calls (no shared AEC reference on the server for every client).
- Sketch a safe track-replacement flow that survives mute and device changes.

## The conferencing audio graph

A simplified local-send path:

```text
Microphone
  → getUserMedia MediaStreamTrack
  → [optional: AudioContext / AudioWorklet NS]
  → [optional: browser APM: AEC / NS / AGC]
  → RTCPeerConnection sender (encode Opus/…)
  → SFU / peers
```

A simplified receive path:

```text
Remote RTP
  → PeerConnection receiver (decode)
  → MediaStreamTrack
  → <audio> / AudioContext render
  → [rarely: post-decode NS on remote — usually wrong place for your own echo]
```

**Product rule of thumb:** run *your* uplink NS on the **local send path**, before encode. Post-decode NS on remote audio cleans *other people's* noise for *your* ears; it does not reduce what you upload.

## Insertion points (A / B / C)

### A — Pre-encode local (recommended for product NS)

Process the mic track, produce a *new* `MediaStreamTrack`, publish that track.

Pros:

- SFU and remote peers receive enhanced speech (bandwidth and ASR benefit).
- One place to tune suppression level for the call.

Cons:

- Adds algorithmic + buffering latency on the critical path.
- Must coexist carefully with AEC (echo path).

### B — Browser APM only

Use `getUserMedia` constraints / Chromium APM (echoCancellation, noiseSuppression, autoGainControl).

Pros: free, low engineering cost, tuned for telephony SNR.

Cons: classical / lighter models; often weaker on non-stationary noise than DeepFilterNet-class models; less control for product UX knobs.

### C — SFU or cloud NS

Server-side enhancement after uplink.

Pros: client CPU free; uniform quality.

Cons: privacy, cost, extra latency; harder AEC; not the Mezon browser-package design.

Mezon's `deepfilternet3-noise-filter` targets **A** via LiveKit `TrackProcessor` (next lesson).

## Browser APM NS vs custom neural NS

| Aspect | APM NS | Custom neural (e.g. DF3 WASM) |
|--------|--------|-------------------------------|
| Control | boolean / browser defaults | suppression level, enable/disable, model version |
| Latency | typically small | frame hop + model (must stay within realtime budget) |
| Quality on keyboard / babble | moderate | often better when model fits domain |
| Echo | AEC inside APM | **You** must not break AEC reference timing |
| Deployment | built-in | WASM + model CDN load |

**Practical combo:** many products keep **AEC + AGC** from the browser and turn **browser NS off** when a neural NS is active, to avoid double-suppression (muffled speech).

Example constraint sketch:

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: false, // neural NS owns this role
    autoGainControl: true,
    channelCount: 1,
  },
});
```

Always verify on the target browser: constraint support and effective settings differ (Chrome vs Safari).

## Track replacement pattern

Conceptual steps:

1. Obtain raw mic track from `getUserMedia`.
2. Feed it through `AudioContext` → worklet/WASM NS → `MediaStreamDestination`.
3. Take `destination.stream.getAudioTracks()[0]` as the **publish track**.
4. On LiveKit: `audioTrack.setProcessor(filter)` (higher-level; lesson 07-02).
5. On raw WebRTC: `sender.replaceTrack(processedTrack)` when switching devices or toggling NS.

```javascript
// Illustrative — not a full product implementation
async function wrapWithPassthroughWorklet(micStream) {
  const ctx = new AudioContext({ sampleRate: 48000 });
  await ctx.audioWorklet.addModule("ns-processor.js");
  const src = ctx.createMediaStreamSource(micStream);
  const worklet = new AudioWorkletNode(ctx, "ns-processor");
  const dest = ctx.createMediaStreamDestination();
  src.connect(worklet).connect(dest);
  return { ctx, track: dest.stream.getAudioTracks()[0] };
}
```

### Device switch and mute

- **Device switch:** tear down old graph (close nodes / destroy processor), rebuild with the new device track, then `replaceTrack`.
- **Mute:** prefer disabling the track or skipping publish; do not leave a stalled worklet without clear UX.
- **Permissions:** re-prompt only when needed; label devices after permission grant.

## Echo path interactions (revisit Chapter 03)

AEC needs a **reference** (what was played to the speaker) aligned with the mic. If your NS:

- adds large unaccounted delay, or
- aggressively alters the mic signal *before* AEC in a browser path that expected a different order,

you can get residual echo or cutouts.

Guidelines:

1. Prefer browser AEC *around* your NS as documented by your stack (LiveKit / browser).
2. Keep NS frame sizes aligned with 10 ms @ 48 kHz when matching DeepFilterNet3 WASM (480 samples) — see Chapter 05.
3. Never run a second full AEC in JS "for luck" without measuring.

## SFU-specific constraints

- The SFU usually **forwards** Opus; it does not share a per-client loudspeaker reference for AEC.
- Simulcast / dynacast: NS CPU is per local participant, not per subscriber.
- If you enable NS only for some clients, document the asymmetry for support teams.

## Worked example: decision matrix

Scenario: Mezon-style meeting app, browser clients, LiveKit SFU.

| Requirement | Choice |
|-------------|--------|
| Clean audio for all listeners | Insertion **A** (local pre-encode) |
| Low engineering time | Start from `DeepFilterNoiseFilterProcessor` |
| Preserve AEC | Keep `echoCancellation: true`; disable browser NS |
| Offline / air-gapped | Bundle WASM+model or private CDN (07-03) |

## Common pitfalls

1. **Double NS** — browser NS + neural NS → dull speech.
2. **Processing remote tracks by default** — wastes CPU; wrong product story for "my noise".
3. **Ignoring sample rate** — resampling before DF3 can hurt quality; prefer 48 kHz graphs.
4. **Leaking AudioContexts** — not closing on leave → device locks / battery drain.
5. **Assuming constraints are honored** — always log `track.getSettings()`.

## Exercises

1. Draw your app's send/receive graph and mark the single NS insertion point you will ship.
2. On Chrome, capture `getSettings()` with NS on vs off; note `noiseSuppression` effective value.
3. List three device-switch edge cases (Bluetooth headset, USB mic, tab background) and how you dispose the processor.
4. Explain in five sentences why SFU-side NS is a different product from Mezon's npm package.

## Further reading

- [WebRTC samples](https://webrtc.github.io/samples/) — track and constraint patterns.
- [MDN: MediaStreamTrack](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack) — `getSettings`, `applyConstraints`, `replaceTrack` via sender.
- WebRTC APM overview in Chromium design docs (search "WebRTC AudioProcessing").
- Course Chapter 03-04 (AEC / APM) and Chapter 05 (AudioWorklet budgets).
