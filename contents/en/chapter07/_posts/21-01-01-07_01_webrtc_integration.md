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

Where you insert noise suppression in a WebRTC call decides latency, echo, and whether the SFU ever forwards clean speech. This lesson maps insertion points against `getUserMedia`, the browser Audio Processing Module, and `RTCPeerConnection`, then shows how `DeepFilterNoiseFilterProcessor` from `deepfilternet3-noise-filter` **1.3.0** occupies the local pre-encode slot through LiveKit’s `TrackProcessor`.

![LiveKit local track passing through a noise-suppression processor before publish]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. Insertion point A is a TrackProcessor on the local mic track, before the sender encodes.*

## Learning objectives

You will place neural noise suppression on the uplink before encode, keep browser echo cancellation while turning browser noise suppression off, and describe what `setProcessor` changes in the published `MediaStreamTrack` without moving inference off the device.

## 60-minute teaching plan

- **0–10 min** — Mic, processing, encode, SFU, decode, render.
- **10–25 min** — Insertion points A, B, and C.
- **25–40 min** — Browser APM versus the 1.3.0 processor.
- **40–50 min** — Device switch, mute, and the worklet graph.
- **50–60 min** — Mini-lab, pitfalls, exercises.

## The conferencing audio graph

A local send path:

```text
Microphone
  → getUserMedia MediaStreamTrack
  → [optional: AudioContext / AudioWorklet NS]
  → [optional: browser APM: AEC / NS / AGC]
  → RTCPeerConnection sender (encode Opus)
  → SFU / peers
```

A receive path:

```text
Remote RTP
  → receiver decode
  → MediaStreamTrack
  → audio element or AudioContext
```

Run **your** uplink noise suppression on the local send path, before encode. Post-decode suppression on a remote track cleans other people’s noise for your ears. It does not reduce what you upload, and it is the wrong place to chase your own echo.

## Insertion points A, B, and C

**A — pre-encode local.** Process the mic and publish the processed track. The SFU and remote peers receive the enhanced speech. You pay algorithmic delay on the critical path, and you must not disturb the echo canceller’s timing. This is the Mezon package’s target. `DeepFilterNoiseFilterProcessor` implements LiveKit’s `TrackProcessor`. You construct it, then `await audioTrack.setProcessor(filter)`, then `await room.localParticipant.publishTrack(audioTrack)`. LiveKit calls the processor’s `init`, which builds the graph. You do not upload PCM to a private enhancement server in this design.

**B — browser APM only.** Constraints such as `echoCancellation`, `noiseSuppression`, and `autoGainControl` ask Chromium’s Audio Processing Module to do the work. Cost is low. Control is mostly a boolean, and non-stationary noise is often weaker than a DeepFilterNet3 model. There is no suppression slider from 0 to 100.

**C — SFU or cloud.** The client CPU stays idle and quality is uniform, at the cost of privacy, money, and extra delay. Echo cancellation also gets harder because the server does not hold each client’s loudspeaker reference. That is a different product from this npm package.

## Browser APM beside the neural path

| Aspect | APM noise suppression | DeepFilterNoiseFilterProcessor |
|--------|----------------------|--------------------------------|
| Control | Boolean / browser default | `noiseReductionLevel`, `setSuppressionLevel` (0–100), `setEnabled` |
| Latency | Usually small | Hop plus model; must meet the real-time factor budget |
| Echo | AEC inside the APM | You keep the AEC reference timing intact |
| Delivery | Built in | WASM plus CDN model (lessons 06-03, 07-03) |

Many products keep **echo cancellation and auto gain** and set **browser noise suppression to false** while the neural processor is active. Two suppressors in series dull the voice. The constraint sketch:

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: false,
    autoGainControl: true,
    channelCount: 1,
  },
});
```

Log `track.getSettings()` on the target browser. Chrome and Safari do not honor every constraint you request.

## What the processor inserts

`DeepFilterNoiseFilterProcessor` is the public LiveKit adapter. `DeepFilterNet3Core` is the Web Audio adapter underneath it. On `init` or `restart` the processor ensures a 48 kHz `AudioContext`, calls `initialize()` (WASM compile and model fetch), and `createAudioWorkletNode`. The graph is source → worklet → `MediaStreamDestination`. `processedTrack` is the destination’s audio track, and that is what LiveKit should publish. `setSuppressionLevel` clamps to an integer from 0 to 100 and posts it to the worklet. `await filter.setEnabled(false)` bypasses suppression without tearing the graph down. `destroy` closes the context and calls `proc.destroy()` on the core.

A raw WebRTC page that does not use LiveKit can build the same graph with `DeepFilterNet3Core` and then `sender.replaceTrack(processedTrack)`. The peer dependency of the package is `livekit-client` ^2; the core class itself is still the right tool when you are not in a Room.

### Device switch and mute

On a device switch, tear the old graph down with `destroy`, or let LiveKit call `restart` with the new `MediaStreamTrack`. Then publish the new processed track. Mute by disabling the track or by `setEnabled(false)`, and keep the UX honest. Do not leave a stalled worklet with no on-screen state. Re-prompt for permission only when the browser requires it.

## Echo, hop, and the SFU

The canceller needs a reference aligned with the microphone. A noise suppressor that adds an unaccounted delay, or that runs in an order the browser AEC did not expect, leaves residual echo or cuts speech. Prefer the stack’s documented AEC, keep the DeepFilter hop near 10 ms at 48 kHz (480 samples) when that is the model’s frame, and do not add a second AEC in JavaScript without a measurement.

The SFU forwards Opus. It does not share a loudspeaker reference for every client. Noise-suppression CPU is per publishing participant, not per subscriber. If only some clients enable it, say so in the support notes.

## Worked choice

For a browser meeting on a LiveKit SFU: insertion **A**, `DeepFilterNoiseFilterProcessor`, `echoCancellation: true`, browser `noiseSuppression: false`, assets from a CDN you control (lesson 07-03) so an air-gapped network is a packaging decision rather than a fork.

## Mini-lab

Run `python3 insertion_check.py`.

```python
steps = [
    "getUserMedia",
    "new DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "publishTrack",
]
constraints = {
    "echoCancellation": True,
    "noiseSuppression": False,
    "autoGainControl": True,
}
print("order=" + " > ".join(steps))
print("browser_ns=" + str(constraints["noiseSuppression"]))
```

**Expected**

```text
order=getUserMedia > new DeepFilterNoiseFilterProcessor > setProcessor > publishTrack
browser_ns=False
```

**Failure modes**

- `noiseSuppression: true` together with the neural processor (double suppression).
- Running the processor on a **remote** track and calling that uplink cleanup.
- Blocking `room.connect()` on the CDN fetch. `setProcessor` waits for `init`, so start the room connection on its own timeline (lesson 07-02).
- `replaceTrack` with the raw mic after a device switch, dropping the processed track on the floor.

## Pitfalls

1. Double noise suppression dulls speech.
2. Processing remote tracks by default spends CPU on the wrong product story.
3. A surprise resample away from 48 kHz before this model.
4. Leaking `AudioContext`s on leave, which holds the microphone and the battery.
5. Assuming constraints were honored because you requested them.

## Exercises

1. Draw your app’s send and receive graph and mark the one insertion point you will ship.
2. On Chrome, capture `getSettings()` with browser noise suppression requested on and off.
3. List three device-switch cases (Bluetooth headset, USB mic, background tab) and name `destroy` or `restart` for each.
4. In five sentences, explain why SFU-side suppression is a different product from this package.
5. Where does `await filter.setEnabled(false)` sit relative to encode, and what still flows to the SFU?

### Answer hints

1. Ship point A on the local mic. Point B is a fallback, not a second stage.
2. Record the effective `noiseSuppression` value, not only the constraint you passed.
3. Bluetooth and USB both need `restart` or a new processor with the new track. A background tab may `suspend` the `AudioContext`; `resume` after the user gesture. Always `destroy` on leave.
4. Cloud suppression sees encoded or server-side audio, costs bandwidth and trust, and lacks the client loudspeaker reference. The npm processor stays in the browser.
5. Bypass is still insertion A. The SFU receives the mic path with suppression disabled, not a different publish slot.

## Further reading

- [WebRTC samples](https://webrtc.github.io/samples/).
- [MDN: MediaStreamTrack](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack).
- LiveKit docs on publish: [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/). Docs home: [https://docs.livekit.io/](https://docs.livekit.io/).
- Chapter 03 for AEC and Chapter 05 for the AudioWorklet budget.
